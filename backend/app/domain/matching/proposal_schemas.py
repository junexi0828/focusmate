"""Pydantic schemas for matching proposals and chat."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Proposal Schemas
class ProposalResponse(BaseModel):
    """Schema for proposal response."""

    proposal_id: UUID
    pool_id_a: UUID
    pool_id_b: UUID
    group_a_status: str
    group_b_status: str
    final_status: str
    chat_room_id: Optional[UUID]
    created_at: datetime
    expires_at: datetime
    matched_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProposalAction(BaseModel):
    """Schema for proposal action (accept/reject)."""

    action: str = Field(..., pattern="^(accept|reject)$")


# Chat Room Schemas
class ChatRoomResponse(BaseModel):
    """Schema for chat room response."""

    room_id: UUID
    room_name: str
    display_mode: str
    group_a_info: dict
    group_b_info: dict
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Message Schemas
class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str = Field(..., min_length=1, max_length=2000)
    message_type: str = Field(default="text", pattern="^(text|image|system)$")
    attachments: Optional[list[str]] = None


class MessageResponse(BaseModel):
    """Schema for message response."""

    message_id: UUID
    room_id: UUID
    sender_id: str
    message_type: str
    content: str
    attachments: Optional[list[str]]
    created_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for message list response."""

    messages: list[MessageResponse]
    total: int
    has_more: bool


# Chat Member Schemas
class ChatMemberResponse(BaseModel):
    """Schema for chat member response."""

    member_id: UUID
    user_id: str
    group_label: str
    member_index: int
    anonymous_name: Optional[str]
    is_active: bool
    last_read_at: Optional[datetime]
    joined_at: datetime

    class Config:
        from_attributes = True
