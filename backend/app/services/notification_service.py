"""Notification service for managing user notifications."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database.models.notification import Notification


class NotificationService:
    """Service for managing notifications with database persistence."""

    def __init__(self, db: AsyncSession):
        """Initialize notification service with database session.

        Args:
            db: Database session for persistence
        """
        self.db = db

    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
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

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_user_notifications(
        self, user_id: str, unread_only: bool = False
    ) -> list[Notification]:
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        query = query.order_by(Notification.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read."""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.notification_id == notification_id,
                    Notification.user_id == user_id
                )
            )
        )
        notification = result.scalar_one_or_none()

        if notification:
            notification.is_read = True
            await self.db.commit()
            return True

        return False

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read."""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
        )
        notifications = result.scalars().all()
        count = 0

        for notification in notifications:
            notification.is_read = True
            count += 1

        await self.db.commit()
        return count

    async def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count."""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
        )
        return len(list(result.scalars().all()))


# Note: NotificationService requires database session
# Use dependency injection: NotificationService(db_session)
