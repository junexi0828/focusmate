"""Participant domain schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ParticipantJoin(BaseModel):
    """Request schema for joining a room."""

    model_config = ConfigDict(strict=True)

    username: str = Field(min_length=1, max_length=50)
    user_id: str | None = None


class ParticipantResponse(BaseModel):
    """Response schema for participant data."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: str
    room_id: str
    user_id: str | None
    username: str
    is_connected: bool
    is_host: bool
    joined_at: datetime
    left_at: datetime | None


class ParticipantListResponse(BaseModel):
    """Response schema for participant list."""

    model_config = ConfigDict(strict=True)

    participants: list[ParticipantResponse]
    total: int
