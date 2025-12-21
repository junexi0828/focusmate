"""Friend ORM Models - friend relationships and requests."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class FriendRequestStatus(str, enum.Enum):
    """Friend request status enum."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class FriendRequest(Base, TimestampMixin):
    """FriendRequest model - tracks friend requests between users."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sender_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    receiver_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        SQLEnum(FriendRequestStatus),
        nullable=False,
        default=FriendRequestStatus.PENDING
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Friend(Base, TimestampMixin):
    """Friend model - represents accepted friendships."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    friend_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
