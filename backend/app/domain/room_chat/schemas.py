"""Schemas for lightweight room chat."""

from datetime import datetime
from pydantic import BaseModel, Field


class RoomChatSend(BaseModel):
    """Inbound chat message payload."""

    content: str = Field(..., min_length=1, max_length=300)


class RoomChatMessage(BaseModel):
    """Outbound chat message payload."""

    id: str
    room_id: str
    sender_id: str
    sender_name: str
    content: str
    created_at: datetime

