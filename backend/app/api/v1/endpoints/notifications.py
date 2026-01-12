"""Notification API endpoints."""


from typing import Annotated, List, Optional
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from app.api.deps import get_current_user_required
from app.api.utils.websocket_auth import extract_ws_token
from app.core.security import decode_jwt_token
from app.domain.notification.schemas import (
    NotificationCreate,
    NotificationMarkRead,
    NotificationResponse,
)
from app.domain.notification.service import NotificationService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.notification_repository import (
    NotificationRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.websocket.notification_manager import notification_ws_manager


router = APIRouter(prefix="/notifications", tags=["notifications"])


# Dependency Injection
def get_notification_repository(db: DatabaseSession) -> NotificationRepository:
    """Get notification repository."""
    return NotificationRepository(db)


def get_user_settings_repository(db: DatabaseSession) -> "UserSettingsRepository":
    """Get user settings repository."""
    from app.infrastructure.repositories.user_settings_repository import (
        UserSettingsRepository,
    )

    return UserSettingsRepository(db)


def get_user_repository(db: DatabaseSession) -> "UserRepository":
    """Get user repository."""
    from app.infrastructure.repositories.user_repository import UserRepository

    return UserRepository(db)


def get_notification_service(
    repo: Annotated[NotificationRepository, Depends(get_notification_repository)],
    settings_repo: Annotated[
        "UserSettingsRepository", Depends(get_user_settings_repository)
    ],
    user_repo: Annotated["UserRepository", Depends(get_user_repository)],
) -> NotificationService:
    """Get notification service with dependencies."""
    return NotificationService(repo, settings_repo, user_repo)


# Endpoints
@router.post(
    "/create", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    data: NotificationCreate,
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> NotificationResponse:
    """Create a new notification (admin or system use).

    Args:
        data: Notification data
        service: Notification service

    Returns:
        Created notification

    Raises:
        HTTPException: If validation fails
    """
    try:
        notification = await service.create_notification(data)

        # If notification is None, it was blocked by user settings
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Notification was not sent due to user settings",
            )

        # Note: Email and push notifications are now handled in NotificationService.create_notification
        return notification
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create notification: {e!s}",
        )


@router.get("/list", response_model=list[NotificationResponse])
async def get_my_notifications(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    unread_only: bool = Query(False, description="Return only unread notifications"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
) -> list[NotificationResponse]:
    """Get notifications for the current user.

    Args:
        current_user: Current authenticated user
        service: Notification service
        unread_only: Whether to return only unread notifications
        limit: Maximum number of notifications to return
        offset: Number of notifications to skip

    Returns:
        List of notifications
    """
    user_id = current_user["id"]
    return await service.get_user_notifications(user_id, unread_only, limit, offset)


@router.get("/backfill", response_model=list[NotificationResponse])
async def get_notification_backfill(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    since: str = Query(..., description="Fetch notifications created after this ISO timestamp"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of notifications"),
) -> list[NotificationResponse]:
    """Get notifications created after a timestamp for reconnection backfill."""
    user_id = current_user["id"]
    try:
        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)",
        ) from e
    return await service.get_notifications_since(user_id, since_dt, limit)


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> dict:
    """Get count of unread notifications for the current user.

    Args:
        current_user: Current authenticated user
        service: Notification service

    Returns:
        Count of unread notifications
    """
    user_id = current_user["id"]
    try:
        count = await service.get_unread_count(user_id)
        return {"unread_count": count}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to get notification unread count for user {user_id}: {e}", exc_info=True)
        # Return 0 to prevent blocking the UI on error
        return {"unread_count": 0}


@router.post("/mark-read", status_code=status.HTTP_200_OK)
async def mark_notifications_as_read(
    data: NotificationMarkRead,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> dict:
    """Mark notifications as read.

    Args:
        data: List of notification IDs to mark as read
        current_user: Current authenticated user
        service: Notification service

    Returns:
        Number of notifications marked as read
    """
    count = await service.mark_as_read(data.notification_ids)
    return {"marked_count": count}


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_as_read(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> dict:
    """Mark all notifications for the current user as read.

    Args:
        current_user: Current authenticated user
        service: Notification service

    Returns:
        Number of notifications marked as read
    """
    user_id = current_user["id"]
    count = await service.mark_all_as_read(user_id)
    return {"marked_count": count}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> None:
    """Delete a notification.

    Args:
        notification_id: Notification identifier
        current_user: Current authenticated user
        service: Notification service

    Raises:
        HTTPException: If notification not found
    """
    success = await service.delete_notification(notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )


@router.websocket("/ws")
async def websocket_notifications(
    websocket: WebSocket,
    db: DatabaseSession,
    token: str | None = Query(None),
):
    """WebSocket endpoint for real-time notifications.

    Args:
        websocket: WebSocket connection
        token: JWT authentication token

    The WebSocket will receive notifications in real-time with the following format:
    {
        "type": "notification",
        "data": {
            "notification_id": "...",
            "type": "...",
            "title": "...",
            "message": "...",
            "data": {...},
            "created_at": "..."
        }
    }
    """
    # Verify token and get user
    try:
        jwt_token = extract_ws_token(websocket, token)
        if not jwt_token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        payload = decode_jwt_token(jwt_token)
        user_id: str | None = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Delegate connection lifecycle (accept, register, subscribe) to manager
    # This handles websocket.accept() internally
    await notification_ws_manager.connect(websocket, user_id)

    try:
        # Send connection confirmation
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to notification stream",
                "user_id": user_id,
            }
        )

        # Keep connection alive and handle incoming messages (e.g., ping/pong)
        while True:
            try:
                data = await websocket.receive_json()

                # Handle ping
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "pong":
                    continue

            except Exception:
                break

    except WebSocketDisconnect:
        notification_ws_manager.disconnect(websocket, user_id)
    except Exception:
        notification_ws_manager.disconnect(websocket, user_id)
