"""Messaging domain schemas."""

from datetime import datetime
from typing import List, Optional

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
    read_at: Optional[datetime]
    created_at: datetime
    sender_username: Optional[str] = None
    receiver_username: Optional[str] = None


# Conversation Schemas
class ConversationResponse(BaseModel):
    """Conversation response schema."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: str
    user1_id: str
    user2_id: str
    last_message_at: Optional[datetime]
    user1_unread_count: int
    user2_unread_count: int
    created_at: datetime
    updated_at: datetime
    other_user_id: Optional[str] = None  # The other participant in conversation
    other_user_username: Optional[str] = None
    last_message: Optional[str] = None


class ConversationListResponse(BaseModel):
    """Simplified conversation list response."""

    id: str
    other_user_id: str
    other_user_username: Optional[str]
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int


class ConversationDetailResponse(BaseModel):
    """Detailed conversation response with messages."""

    conversation: ConversationResponse
    messages: List[MessageResponse]


# Mark as Read
class MarkMessagesReadRequest(BaseModel):
    """Request to mark messages as read."""

    message_ids: List[str] = Field(..., min_length=1)


class MarkMessagesReadResponse(BaseModel):
    """Response after marking messages as read."""

    marked_count: int
    conversation_id: str
    new_unread_count: int
