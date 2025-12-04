"""Participant ORM Model.

Represents a user participating in a room.
Tracks connection status and join/leave timestamps.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class Participant(Base, TimestampMixin):
    """Participant model - represents a user in a room.

    Attributes:
        id: Unique participant identifier (UUID)
        room_id: Associated room ID
        user_id: User identifier (optional, for anonymous users)
        username: Display name
        is_connected: WebSocket connection status
        is_host: Whether this participant is the room host
        joined_at: Join timestamp
        left_at: Leave timestamp (null if still in room)
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Unique participant identifier (UUID)",
    )

    room_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="Associated room ID",
    )

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        comment="User ID (optional for anonymous)",
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Display name",
    )

    is_connected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Connection status",
    )

    is_host: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Is room host",
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Join timestamp",
    )

    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Leave timestamp",
    )

    def __repr__(self) -> str:
        """String representation of Participant."""
        return (
            f"<Participant(id={self.id}, username={self.username}, "
            f"room_id={self.room_id})>"
        )
