"""Matching pool database models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ARRAY, Boolean, CheckConstraint, ForeignKey, Integer, JSON, String, Text, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class MatchingPool(Base):
    """Matching pool model for group matching."""

    __tablename__ = "matching_pools"

    pool_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    creator_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Group information
    member_count: Mapped[int] = mapped_column(Integer(), nullable=False)
    member_ids: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)

    # Department information
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)

    # Matching preferences
    preferred_match_type: Mapped[str] = mapped_column(String(20), nullable=False)
    preferred_categories: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text()), nullable=True
    )

    # Display settings
    matching_type: Mapped[str] = mapped_column(String(10), nullable=False)

    # Message
    message: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'waiting'")
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP + INTERVAL '7 days'"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        CheckConstraint("member_count >= 2 AND member_count <= 8", name="check_member_count"),
        CheckConstraint("char_length(message) <= 200", name="check_message_length"),
    )

    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])

    def __repr__(self) -> str:
        return f"<MatchingPool(pool_id={self.pool_id}, status={self.status})>"


class MatchingProposal(Base):
    """Matching proposal model."""

    __tablename__ = "matching_proposals"

    proposal_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    pool_id_a: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("matching_pools.pool_id", ondelete="CASCADE"),
        nullable=False,
    )
    pool_id_b: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("matching_pools.pool_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Acceptance status
    group_a_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pending'")
    )
    group_b_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pending'")
    )

    # Final status
    final_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pending'")
    )

    # Chat room
    chat_room_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQL_UUID(as_uuid=True), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP + INTERVAL '24 hours'"),
    )
    matched_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint("pool_id_a", "pool_id_b", name="uq_matching_proposals_pools"),
    )

    # Relationships
    pool_a: Mapped["MatchingPool"] = relationship(
        "MatchingPool", foreign_keys=[pool_id_a]
    )
    pool_b: Mapped["MatchingPool"] = relationship(
        "MatchingPool", foreign_keys=[pool_id_b]
    )

    def __repr__(self) -> str:
        return f"<MatchingProposal(proposal_id={self.proposal_id}, status={self.final_status})>"


class MatchingChatRoom(Base):
    """Matching chat room model."""

    __tablename__ = "matching_chat_rooms"

    room_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    proposal_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("matching_proposals.proposal_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Room information
    room_name: Mapped[str] = mapped_column(String(200), nullable=False)
    display_mode: Mapped[str] = mapped_column(String(10), nullable=False)

    # Group information
    group_a_info: Mapped[dict] = mapped_column(JSON(), nullable=False)
    group_b_info: Mapped[dict] = mapped_column(JSON(), nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("true")
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    proposal: Mapped["MatchingProposal"] = relationship("MatchingProposal")
    members: Mapped[list["MatchingChatMember"]] = relationship(
        "MatchingChatMember", back_populates="room"
    )
    messages: Mapped[list["MatchingMessage"]] = relationship(
        "MatchingMessage", back_populates="room"
    )

    def __repr__(self) -> str:
        return f"<MatchingChatRoom(room_id={self.room_id}, name={self.room_name})>"


class MatchingChatMember(Base):
    """Matching chat member model."""

    __tablename__ = "matching_chat_members"

    member_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    room_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("matching_chat_rooms.room_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Group identification
    group_label: Mapped[str] = mapped_column(String(10), nullable=False)
    member_index: Mapped[int] = mapped_column(Integer(), nullable=False)

    # Anonymous name
    anonymous_name: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("true")
    )
    last_read_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)

    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)

    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="uq_matching_chat_members_room_user"),
    )

    # Relationships
    room: Mapped["MatchingChatRoom"] = relationship(
        "MatchingChatRoom", back_populates="members"
    )

    def __repr__(self) -> str:
        return f"<MatchingChatMember(member_id={self.member_id}, user_id={self.user_id})>"


class MatchingMessage(Base):
    """Matching message model."""

    __tablename__ = "matching_messages"

    message_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    room_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("matching_chat_rooms.room_id", ondelete="CASCADE"),
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

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)

    # Relationships
    room: Mapped["MatchingChatRoom"] = relationship(
        "MatchingChatRoom", back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<MatchingMessage(message_id={self.message_id}, type={self.message_type})>"
