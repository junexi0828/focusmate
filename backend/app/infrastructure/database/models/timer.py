"""Timer ORM Model.

Represents the timer state for a room.
Server-authoritative design: timer state is managed by backend.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin
from app.shared.constants.timer import TimerPhase, TimerStatus


class Timer(Base, TimestampMixin):
    """Timer model - represents the current timer state for a room.

    Server-Authoritative Design:
    - Timer calculations are performed on the backend
    - Clients receive authoritative state via WebSocket
    - Prevents client-side drift and tampering

    Attributes:
        id: Unique timer identifier (UUID)
        room_id: Associated room ID (foreign key reference)
        status: Current timer status (IDLE, RUNNING, PAUSED, COMPLETED)
        phase: Current phase (WORK, BREAK)
        duration: Total duration for current phase (seconds)
        remaining_seconds: Remaining time (seconds)
        started_at: Timestamp when timer started
        paused_at: Timestamp when timer paused
        completed_at: Timestamp when timer completed
        is_auto_start: Auto-start next phase
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Unique timer identifier (UUID)",
    )

    room_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
        comment="Associated room ID",
    )

    status: Mapped[str] = mapped_column(
        SQLEnum(TimerStatus, native_enum=False, length=20),
        nullable=False,
        default=TimerStatus.IDLE.value,
        index=True,
        comment="Timer status",
    )

    phase: Mapped[str] = mapped_column(
        SQLEnum(TimerPhase, native_enum=False, length=20),
        nullable=False,
        default=TimerPhase.WORK.value,
        comment="Current phase",
    )

    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1500,  # 25 minutes in seconds
        comment="Total duration (seconds)",
    )

    remaining_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1500,
        comment="Remaining time (seconds)",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Start timestamp",
    )

    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Pause timestamp",
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Completion timestamp",
    )

    is_auto_start: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Auto-start next phase",
    )

    def __repr__(self) -> str:
        """String representation of Timer."""
        return (
            f"<Timer(id={self.id}, room_id={self.room_id}, "
            f"status={self.status}, phase={self.phase})>"
        )
