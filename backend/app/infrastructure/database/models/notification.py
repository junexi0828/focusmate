"""Notification ORM Model."""


from typing import Optional
from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin
from datetime import datetime


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

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        comment="Priority: high, medium, low",
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

    routing: Mapped[dict | None] = mapped_column(
        JSON(),
        nullable=True,
        comment="Frontend routing info: {path, params}",
    )

    group_key: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Key for grouping similar notifications",
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether the notification has been read",
    )

    read_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="Timestamp when notification was read",
    )

    delivered_via_ws: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Delivered via WebSocket",
    )

    delivered_via_email: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Delivered via Email",
    )

    __table_args__ = (
        Index('idx_user_unread', 'user_id', 'is_read'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Notification(notification_id={self.notification_id}, user_id={self.user_id}, type={self.type})>"

