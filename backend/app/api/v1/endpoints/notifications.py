"""Notification API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
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
        return await service.create_notification(data)
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
