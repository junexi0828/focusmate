"""Pydantic schemas for unified chat system."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Room Schemas
class ChatRoomCreate(BaseModel):
    """Schema for creating a chat room."""

    room_type: Literal["direct", "team", "matching"]
    room_name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None
    display_mode: Optional[Literal["open", "blind"]] = None


class ChatRoomResponse(BaseModel):
    """Schema for chat room response."""

    room_id: UUID
    room_type: str
    room_name: Optional[str]
    description: Optional[str]
    metadata: Optional[dict] = Field(
        None, alias="room_metadata"
    )  # Maps from room_metadata
    display_mode: Optional[str]
    is_active: bool
    is_archived: bool
    created_at: datetime
    last_message_at: Optional[datetime]
    last_message_content: Optional[str] = None  # Last message preview
    last_message_sender_id: Optional[str] = None  # Last message sender
    unread_count: int = 0  # Calculated field

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both metadata and room_metadata


class ChatRoomListResponse(BaseModel):
    """Schema for chat room list response."""

    rooms: list[ChatRoomResponse]
    total: int


# Member Schemas
class ChatMemberResponse(BaseModel):
    """Schema for chat member response."""

    member_id: UUID
    user_id: str
    role: str
    display_name: Optional[str]
    anonymous_name: Optional[str]
    group_label: Optional[str]
    member_index: Optional[int]
    is_active: bool
    is_muted: bool
    last_read_at: Optional[datetime]
    unread_count: int
    joined_at: datetime

    class Config:
        from_attributes = True


# Message Schemas
class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str = Field(..., min_length=1, max_length=5000)
    message_type: Literal["text", "image", "file", "system"] = "text"
    attachments: Optional[list[str]] = None
    parent_message_id: Optional[UUID] = None


class MessageUpdate(BaseModel):
    """Schema for updating a message."""

    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    """Schema for message response."""

    message_id: UUID
    room_id: UUID
    sender_id: str
    message_type: str
    content: str
    attachments: Optional[list[str]]
    parent_message_id: Optional[UUID]
    thread_count: int
    reactions: list
    is_edited: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for message list response."""

    messages: list[MessageResponse]
    total: int
    has_more: bool


# Direct Chat Schemas
class DirectChatCreate(BaseModel):
    """Schema for creating a direct chat."""

    recipient_id: str = Field(..., min_length=1)


# Team Chat Schemas
class TeamChatCreate(BaseModel):
    """Schema for creating a team chat."""

    team_id: UUID
    room_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


# Matching Chat Schemas (created automatically from proposals)
class MatchingChatInfo(BaseModel):
    """Schema for matching chat information."""

    proposal_id: UUID
    group_a_info: dict
    group_b_info: dict
    display_mode: Literal["open", "blind"]


# Read Status Schema
class ReadStatusUpdate(BaseModel):
    """Schema for updating read status."""

    last_message_id: Optional[UUID] = None
