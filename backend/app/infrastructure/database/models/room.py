"""Room ORM Model.

Represents a team room where users collaborate with synchronized timers.
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class Room(Base, TimestampMixin):
    """Room model - represents a collaborative Pomodoro room.

    Attributes:
        id: Unique room identifier (UUID)
        name: Room name (3-50 characters)
        work_duration: Focus time in minutes (1-60)
        break_duration: Break time in minutes (1-30)
        auto_start_break: Auto-start break after focus
        is_active: Room active status
        host_id: Room creator identifier (optional, for future auth)
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Unique room identifier (UUID)",
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Room name",
    )

    work_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=25,
        comment="Focus time in minutes",
    )

    break_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        comment="Break time in minutes",
    )

    auto_start_break: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Auto-start break after focus",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Room active status",
    )

    host_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        comment="Room host user ID (optional)",
    )

    def __repr__(self) -> str:
        """String representation of Room."""
        return f"<Room(id={self.id}, name={self.name})>"
