"""Messaging domain schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Message Schemas
class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    receiver_id: str = Field(..., min_length=1, max_length=36)
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    """Message response schema."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: str
    conversation_id: str
    sender_id: str
    receiver_id: str
    content: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime
    sender_username: str | None = None
    receiver_username: str | None = None


# Conversation Schemas
class ConversationResponse(BaseModel):
    """Conversation response schema."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: str
    user1_id: str
    user2_id: str
    last_message_at: datetime | None
    user1_unread_count: int
    user2_unread_count: int
    created_at: datetime
    updated_at: datetime
    other_user_id: str | None = None  # The other participant in conversation
    other_user_username: str | None = None
    last_message: str | None = None


class ConversationListResponse(BaseModel):
    """Simplified conversation list response."""

    id: str
    other_user_id: str
    other_user_username: str | None
    last_message: str | None
    last_message_at: datetime | None
    unread_count: int


class ConversationDetailResponse(BaseModel):
    """Detailed conversation response with messages."""

    conversation: ConversationResponse
    messages: list[MessageResponse]


# Mark as Read
class MarkMessagesReadRequest(BaseModel):
    """Request to mark messages as read."""

    message_ids: list[str] = Field(..., min_length=1)


class MarkMessagesReadResponse(BaseModel):
    """Response after marking messages as read."""

    marked_count: int
    conversation_id: str
    new_unread_count: int
