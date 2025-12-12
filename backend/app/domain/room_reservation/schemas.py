"""Room Reservation domain schemas (Request/Response DTOs)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoomReservationCreate(BaseModel):
    """Request schema for creating a room reservation."""

    model_config = ConfigDict(strict=True)

    scheduled_at: datetime = Field(..., description="When the room session should start")
    work_duration: int = Field(
        default=25 * 60, ge=60, le=3600, description="Focus time in seconds"
    )
    break_duration: int = Field(
        default=5 * 60, ge=60, le=1800, description="Break time in seconds"
    )
    description: str | None = Field(None, max_length=500, description="Optional description")


class RoomReservationUpdate(BaseModel):
    """Request schema for updating a room reservation."""

    model_config = ConfigDict(strict=True)

    scheduled_at: datetime | None = Field(None, description="When the room session should start")
    work_duration: int | None = Field(None, ge=60, le=3600, description="Focus time in seconds")
    break_duration: int | None = Field(
        None, ge=60, le=1800, description="Break time in seconds"
    )
    description: str | None = Field(None, max_length=500, description="Optional description")


class RoomReservationResponse(BaseModel):
    """Response schema for room reservation data."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: str
    room_id: str | None
    user_id: str
    scheduled_at: datetime
    work_duration: int
    break_duration: int
    description: str | None
    is_active: bool
    is_completed: bool
    created_at: datetime
    updated_at: datetime

