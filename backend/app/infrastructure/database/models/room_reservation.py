"""Room Reservation ORM Model.

Represents a scheduled room reservation for future sessions.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class RoomReservation(Base, TimestampMixin):
    """Room reservation model - represents a scheduled room session.

    Attributes:
        id: Unique reservation identifier (UUID)
        room_id: Associated room ID
        user_id: User who made the reservation
        scheduled_at: When the room session should start
        work_duration: Focus time in seconds
        break_duration: Break time in seconds
        description: Optional description/notes
        is_active: Whether reservation is still active
        is_completed: Whether the session has been completed
    """

    __tablename__ = "room_reservations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Unique reservation identifier (UUID)",
    )

    room_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        comment="Associated room ID (null if room not created yet)",
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="User who made the reservation",
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When the room session should start",
    )

    work_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=25 * 60,  # 25 minutes in seconds
        comment="Focus time in seconds",
    )

    break_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5 * 60,  # 5 minutes in seconds
        comment="Break time in seconds",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Optional description/notes",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether reservation is still active",
    )

    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether the session has been completed",
    )

    recurrence_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default="none",
        comment="Recurrence pattern: none, daily, weekly, monthly",
    )

    recurrence_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When to stop creating recurring reservations",
    )

    notification_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        comment="Minutes before scheduled time to send notification",
    )

    notification_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether notification has been sent",
    )

    def __repr__(self) -> str:
        """String representation of RoomReservation."""
        return (
            f"<RoomReservation(id={self.id}, user_id={self.user_id}, "
            f"scheduled_at={self.scheduled_at})>"
        )

