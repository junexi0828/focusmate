"""User presence tracking database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class UserPresence(Base):
    """User online/offline presence tracking."""

    __tablename__ = "user_presence"

    # user_id as primary key
    id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Online status
    is_online: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("false")
    )

    # Last activity timestamp
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Connection count (supports multiple devices)
    connection_count: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default=text("0")
    )

    # Optional status message
    status_message: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
