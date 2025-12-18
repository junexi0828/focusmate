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
    work_duration: int = Field(
        ge=MIN_WORK_DURATION * 60,  # Convert minutes to seconds
        le=MAX_WORK_DURATION * 60,  # Convert minutes to seconds
        default=25 * 60,  # 25 minutes in seconds
    )
    break_duration: int = Field(
        ge=MIN_BREAK_DURATION * 60,  # Convert minutes to seconds
        le=MAX_BREAK_DURATION * 60,  # Convert minutes to seconds
        default=5 * 60,  # 5 minutes in seconds
    )
    auto_start_break: bool = True
    remove_on_leave: bool = Field(
        default=False,
        description="If true, participants are removed from room list when they leave. If false, participants remain visible even after leaving.",
    )


class RoomUpdate(BaseModel):
    """Request schema for updating room settings."""

    model_config = ConfigDict(strict=True)

    work_duration: int | None = Field(
        None,
        ge=MIN_WORK_DURATION * 60,  # Convert minutes to seconds
        le=MAX_WORK_DURATION * 60,  # Convert minutes to seconds
    )
    break_duration: int | None = Field(
        None,
        ge=MIN_BREAK_DURATION * 60,  # Convert minutes to seconds
        le=MAX_BREAK_DURATION * 60,  # Convert minutes to seconds
    )
    auto_start_break: bool | None = None
    remove_on_leave: bool | None = Field(
        None,
        description="If true, participants are removed from room list when they leave. If false, participants remain visible even after leaving.",
    )


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
    remove_on_leave: bool = False
    created_at: datetime
    updated_at: datetime
