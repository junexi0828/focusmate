"""Pydantic schemas for unified chat system."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# Room Schemas
class ChatRoomCreate(BaseModel):
    """Schema for creating a chat room."""

    room_type: Literal["direct", "team", "matching"]
    room_name: str | None = None
    description: str | None = None
    metadata: dict | None = None
    display_mode: Literal["open", "blind"] | None = None


class ChatRoomResponse(BaseModel):
    """Schema for chat room response."""

    room_id: UUID
    room_type: str
    room_name: str | None
    description: str | None
    metadata: dict | None = Field(
        None, alias="room_metadata"
    )  # Maps from room_metadata
    display_mode: str | None
    is_active: bool
    is_archived: bool
    created_at: datetime
    last_message_at: datetime | None
    last_message_content: str | None = None  # Last message preview
    last_message_sender_id: str | None = None  # Last message sender
    unread_count: int = 0  # Calculated field

    # Direct chat partner info (for direct chats only)
    partner_id: str | None = None
    partner_username: str | None = None
    partner_email: str | None = None
    partner_profile_image: str | None = None
    partner_is_online: bool | None = None

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
    display_name: str | None
    anonymous_name: str | None
    group_label: str | None
    member_index: int | None
    is_active: bool
    is_muted: bool
    last_read_at: datetime | None
    unread_count: int
    joined_at: datetime

    class Config:
        from_attributes = True


# Message Schemas
class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str = Field(..., min_length=1, max_length=5000)
    message_type: Literal["text", "image", "file", "system"] = "text"
    attachments: list[str] | None = None
    parent_message_id: UUID | None = None


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
    attachments: list[str] | None
    parent_message_id: UUID | None
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
    description: str | None = None


class TeamChatCreateByEmail(BaseModel):
    """Schema for creating a team chat by email addresses."""

    room_name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    member_emails: list[str] = Field(..., min_items=1, max_items=50)
    send_invitations: bool = True  # Whether to send email invitations


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

    last_message_id: UUID | None = None


# Invitation Code Schemas
class InvitationCodeInfo(BaseModel):
    """Schema for invitation code information."""

    code: str
    room_id: UUID
    expires_at: datetime | None
    max_uses: int | None
    current_uses: int
    is_valid: bool

    class Config:
        from_attributes = True


class InvitationCodeCreate(BaseModel):
    """Schema for creating invitation code."""

    expires_hours: int = Field(24, ge=1, le=168)  # 1 hour to 7 days
    max_uses: int | None = Field(None, ge=1, le=100)


class InvitationJoinRequest(BaseModel):
    """Schema for joining room via invitation code."""

    invitation_code: str = Field(..., min_length=8, max_length=8)


class FriendRoomCreate(BaseModel):
    """Schema for creating room with friends."""

    friend_ids: list[str] = Field(..., min_length=1, max_length=10)
    room_name: str | None = Field(None, max_length=200)
    description: str | None = None
    generate_invitation: bool = False
    invitation_expires_hours: int = Field(24, ge=1, le=168)
