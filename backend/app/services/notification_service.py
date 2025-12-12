"""Notification system for chat events."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class NotificationType(str, Enum):
    """Notification types."""

    MESSAGE = "message"
    MENTION = "mention"
    REACTION = "reaction"
    PROPOSAL = "proposal"
    SYSTEM = "system"


class Notification(BaseModel):
    """Notification model."""

    notification_id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None
    is_read: bool = False
    created_at: datetime


class NotificationService:
    """Service for managing notifications."""

    def __init__(self):
        # In-memory storage (replace with database in production)
        self.notifications: dict[str, list[Notification]] = {}

    def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[dict] = None,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            notification_id=str(uuid4()),
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data,
            created_at=datetime.utcnow(),
        )

        if user_id not in self.notifications:
            self.notifications[user_id] = []

        self.notifications[user_id].append(notification)
        return notification

    def get_user_notifications(
        self, user_id: str, unread_only: bool = False
    ) -> list[Notification]:
        """Get notifications for a user."""
        notifications = self.notifications.get(user_id, [])

        if unread_only:
            notifications = [n for n in notifications if not n.is_read]

        return sorted(notifications, key=lambda n: n.created_at, reverse=True)

    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read."""
        notifications = self.notifications.get(user_id, [])

        for notification in notifications:
            if notification.notification_id == notification_id:
                notification.is_read = True
                return True

        return False

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read."""
        notifications = self.notifications.get(user_id, [])
        count = 0

        for notification in notifications:
            if not notification.is_read:
                notification.is_read = True
                count += 1

        return count

    def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count."""
        notifications = self.notifications.get(user_id, [])
        return sum(1 for n in notifications if not n.is_read)


# Global notification service instance
notification_service = NotificationService()
