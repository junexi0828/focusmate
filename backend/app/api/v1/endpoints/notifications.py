"""Notification API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect

from app.api.deps import get_current_user
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
from app.infrastructure.websocket.notification_manager import notification_ws_manager

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Dependency Injection
def get_notification_repository(db: DatabaseSession) -> NotificationRepository:
    """Get notification repository."""
    return NotificationRepository(db)


def get_notification_service(
    repo: Annotated[NotificationRepository, Depends(get_notification_repository)],
) -> NotificationService:
    """Get notification service."""
    return NotificationService(repo)


# Endpoints
@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
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

        # Send real-time notification via WebSocket if user is online
        await notification_ws_manager.send_notification(
            {
                "type": "notification",
                "data": {
                    "notification_id": notification.notification_id,
                    "type": notification.type,
                    "title": notification.title,
                    "message": notification.message,
                    "data": notification.data,
                    "created_at": notification.created_at.isoformat(),
                },
            },
            notification.user_id,
        )

        return notification
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create notification: {str(e)}",
        )


@router.get("/", response_model=list[NotificationResponse])
async def get_my_notifications(
    current_user: Annotated[dict, Depends(get_current_user)],
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


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: Annotated[dict, Depends(get_current_user)],
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
    count = await service.get_unread_count(user_id)
    return {"unread_count": count}


@router.post("/mark-read", status_code=status.HTTP_200_OK)
async def mark_notifications_as_read(
    data: NotificationMarkRead,
    current_user: Annotated[dict, Depends(get_current_user)],
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
    current_user: Annotated[dict, Depends(get_current_user)],
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
    current_user: Annotated[dict, Depends(get_current_user)],
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
    token: str = Query(...),
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
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connect user
    await notification_ws_manager.connect(websocket, user_id)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to notification stream",
            "user_id": user_id,
        })

        # Keep connection alive and handle incoming messages (e.g., ping/pong)
        while True:
            try:
                data = await websocket.receive_json()

                # Handle ping
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except Exception:
                break

    except WebSocketDisconnect:
        notification_ws_manager.disconnect(websocket, user_id)
    except Exception:
        notification_ws_manager.disconnect(websocket, user_id)
