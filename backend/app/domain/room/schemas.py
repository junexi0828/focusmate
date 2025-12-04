"""Room domain schemas (Request/Response DTOs)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.shared.constants.timer import (
    MAX_BREAK_DURATION,
    MAX_ROOM_NAME_LENGTH,
    MAX_WORK_DURATION,
    MIN_BREAK_DURATION,
    MIN_ROOM_NAME_LENGTH,
    MIN_WORK_DURATION,
)


class RoomCreate(BaseModel):
    """Request schema for creating a room."""

    model_config = ConfigDict(strict=True)

    name: str = Field(
        min_length=MIN_ROOM_NAME_LENGTH,
        max_length=MAX_ROOM_NAME_LENGTH,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    work_duration: int = Field(ge=MIN_WORK_DURATION, le=MAX_WORK_DURATION, default=25)
    break_duration: int = Field(ge=MIN_BREAK_DURATION, le=MAX_BREAK_DURATION, default=5)
    auto_start_break: bool = True


class RoomUpdate(BaseModel):
    """Request schema for updating room settings."""

    model_config = ConfigDict(strict=True)

    work_duration: int | None = Field(None, ge=MIN_WORK_DURATION, le=MAX_WORK_DURATION)
    break_duration: int | None = Field(None, ge=MIN_BREAK_DURATION, le=MAX_BREAK_DURATION)
    auto_start_break: bool | None = None


class RoomResponse(BaseModel):
    """Response schema for room data."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: str
    name: str
    work_duration: int
    break_duration: int
    auto_start_break: bool
    is_active: bool
    host_id: str | None
    created_at: datetime
    updated_at: datetime
