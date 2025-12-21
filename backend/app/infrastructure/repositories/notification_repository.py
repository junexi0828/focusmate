"""Notification repository."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.notification import Notification


class NotificationRepository:
    """Repository for notification operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository."""
        self.db = db

    async def create(self, notification: Notification) -> Notification:
        """Create a new notification.

        Args:
            notification: Notification to create

        Returns:
            Created notification
        """
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: str) -> Notification | None:
        """Get notification by ID.

        Args:
            notification_id: Notification identifier

        Returns:
            Notification if found, None otherwise
        """
        result = await self.db.execute(
            select(Notification).where(
                Notification.notification_id == notification_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """Get notifications for a user.

        Args:
            user_id: User identifier
            unread_only: Whether to return only unread notifications
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip

        Returns:
            List of notifications
        """
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        query = (
            query.order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, notification: Notification) -> Notification:
        """Update a notification.

        Args:
            notification: Notification to update

        Returns:
            Updated notification
        """
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def delete(self, notification: Notification) -> None:
        """Delete a notification.

        Args:
            notification: Notification to delete
        """
        await self.db.delete(notification)
        await self.db.commit()

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read.

        Args:
            user_id: User identifier

        Returns:
            Number of notifications marked as read
        """
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.db.commit()
        return result.rowcount

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user.

        Args:
            user_id: User identifier

        Returns:
            Count of unread notifications
        """
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id, Notification.is_read == False
            )
        )
        return len(list(result.scalars().all()))
