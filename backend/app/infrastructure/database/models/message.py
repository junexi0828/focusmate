"""Message ORM Models - conversations and messages."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class Conversation(Base, TimestampMixin):
    """Conversation model - represents a 1:1 chat between two users."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user1_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user2_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user1_unread_count: Mapped[int] = mapped_column(Integer, default=0)
    user2_unread_count: Mapped[int] = mapped_column(Integer, default=0)


class Message(Base, TimestampMixin):
    """Message model - individual messages within conversations."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sender_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    receiver_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
