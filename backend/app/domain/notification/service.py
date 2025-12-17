"""Notification domain service."""

from datetime import datetime
from typing import Optional

from app.core.exceptions import ValidationException
from app.domain.notification.schemas import (
    NotificationCreate,
    NotificationResponse,
)
from app.infrastructure.database.models.notification import Notification
from app.infrastructure.repositories.notification_repository import (
    NotificationRepository,
)
from app.shared.utils.uuid import generate_uuid


class NotificationService:
    """Notification service for managing user notifications."""

    def __init__(self, repository: NotificationRepository) -> None:
        """Initialize service."""
        self.repository = repository

    async def create_notification(
        self, data: NotificationCreate
    ) -> NotificationResponse:
        """Create a new notification.

        Args:
            data: Notification data

        Returns:
            Created notification

        Raises:
            ValidationException: If validation fails
        """
        notification = Notification(
            notification_id=generate_uuid(),
            user_id=data.user_id,
            type=data.type,
            title=data.title,
            message=data.message,
            data=data.data,
            is_read=False,
        )

        created = await self.repository.create(notification)
        return NotificationResponse.model_validate(created)

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[NotificationResponse]:
        """Get notifications for a user.

        Args:
            user_id: User identifier
            unread_only: Whether to return only unread notifications
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip

        Returns:
            List of notifications
        """
        notifications = await self.repository.get_by_user(
            user_id, unread_only, limit, offset
        )
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def mark_as_read(self, notification_ids: list[str]) -> int:
        """Mark notifications as read.

        Args:
            notification_ids: List of notification IDs to mark as read

        Returns:
            Number of notifications marked as read
        """
        count = 0
        for notification_id in notification_ids:
            notification = await self.repository.get_by_id(notification_id)
            if notification and not notification.is_read:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                await self.repository.update(notification)
                count += 1
        return count

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read.

        Args:
            user_id: User identifier

        Returns:
            Number of notifications marked as read
        """
        return await self.repository.mark_all_as_read(user_id)

    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification.

        Args:
            notification_id: Notification identifier

        Returns:
            True if deleted successfully
        """
        notification = await self.repository.get_by_id(notification_id)
        if not notification:
            return False

        await self.repository.delete(notification)
        return True

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user.

        Args:
            user_id: User identifier

        Returns:
            Count of unread notifications
        """
        return await self.repository.get_unread_count(user_id)
