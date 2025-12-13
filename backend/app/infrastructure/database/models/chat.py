"""Unified chat system database models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class ChatRoom(Base):
    """Unified chat room model for all chat types."""

    __tablename__ = "chat_rooms"

    room_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # Room type
    room_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Room information
    room_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    # Type-specific metadata (renamed from 'metadata' to avoid SQLAlchemy reserved word)
    room_metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata", JSON(), nullable=True
    )

    # Display settings
    display_mode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("true")
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("false")
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    members: Mapped[list["ChatMember"]] = relationship(
        "ChatMember", back_populates="room", cascade="all, delete-orphan"
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="room", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChatRoom(room_id={self.room_id}, type={self.room_type})>"


class ChatMember(Base):
    """Unified chat member model for all participants."""

    __tablename__ = "chat_members"

    member_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    room_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("chat_rooms.room_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Member role
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'member'")
    )

    # Display name
    display_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    anonymous_name: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Group identification (for matching)
    group_label: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    member_index: Mapped[Optional[int]] = mapped_column(Integer(), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("true")
    )
    is_muted: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("false")
    )

    # Read status
    last_read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    unread_count: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default=text("0")
    )

    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="uq_chat_members_room_user"),
    )

    # Relationships
    room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="members")

    def __repr__(self) -> str:
        return f"<ChatMember(member_id={self.member_id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """Unified chat message model for all messages."""

    __tablename__ = "chat_messages"

    message_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    room_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("chat_rooms.room_id", ondelete="CASCADE"),
        nullable=False,
    )
    sender_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Message content
    message_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'text'")
    )
    content: Mapped[str] = mapped_column(Text(), nullable=False)

    # Attachments
    attachments: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text()), nullable=True
    )

    # Reply/Thread
    parent_message_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("chat_messages.message_id", ondelete="SET NULL"),
        nullable=True,
    )
    thread_count: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default=text("0")
    )

    # Reactions
    reactions: Mapped[list[dict]] = mapped_column(
        JSON(), nullable=False, server_default=text("'[]'")
    )

    # Status
    is_edited: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("false")
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("false")
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="messages")
    parent: Mapped[Optional["ChatMessage"]] = relationship(
        "ChatMessage", remote_side=[message_id], foreign_keys=[parent_message_id]
    )

    def __repr__(self) -> str:
        return f"<ChatMessage(message_id={self.message_id}, type={self.message_type})>"
