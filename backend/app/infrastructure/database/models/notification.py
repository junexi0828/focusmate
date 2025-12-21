"""Notification ORM Model."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class Notification(Base, TimestampMixin):
    """Notification model for user notifications."""

    __tablename__ = "notifications"

    notification_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Unique notification identifier (UUID)",
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who receives the notification",
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Notification type (e.g., 'system', 'achievement', 'message')",
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Notification title",
    )

    message: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
        comment="Notification message content",
    )

    data: Mapped[dict | None] = mapped_column(
        JSON(),
        nullable=True,
        comment="Additional notification data (JSON)",
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the notification has been read",
    )

    read_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="Timestamp when notification was read",
    )

    def __repr__(self) -> str:
        return f"<Notification(notification_id={self.notification_id}, user_id={self.user_id}, type={self.type})>"

