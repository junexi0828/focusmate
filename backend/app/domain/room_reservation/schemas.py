"""Room Reservation domain schemas (Request/Response DTOs)."""

from datetime import datetime
from typing import Optional, Union
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RecurrenceType(str, Enum):
    """Recurrence type for reservations."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RoomReservationCreate(BaseModel):
    """Request schema for creating a room reservation."""

    model_config = ConfigDict(strict=False)  # Allow string to datetime conversion

    scheduled_at: datetime = Field(..., description="When the room session should start")
    work_duration: int = Field(
        default=25 * 60, ge=60, le=3600, description="Focus time in seconds"
    )
    break_duration: int = Field(
        default=5 * 60, ge=60, le=1800, description="Break time in seconds"
    )
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    recurrence_type: Union[RecurrenceType, str] = Field(
        default=RecurrenceType.NONE, description="Recurrence pattern"
    )
    recurrence_end_date: Union[datetime, Optional][str] = Field(
        None, description="When to stop creating recurring reservations"
    )
    notification_minutes: int = Field(
        default=5, ge=0, le=60, description="Minutes before scheduled time to send notification"
    )


class RoomReservationUpdate(BaseModel):
    """Request schema for updating a room reservation."""

    model_config = ConfigDict(strict=True)

    scheduled_at: Optional[datetime] = Field(None, description="When the room session should start")
    work_duration: Optional[int] = Field(None, ge=60, le=3600, description="Focus time in seconds")
    break_duration: Optional[int] = Field(
        None, ge=60, le=1800, description="Break time in seconds"
    )
    description: Optional[str] = Field(None, max_length=500, description="Optional description")


class RoomReservationResponse(BaseModel):
    """Response schema for room reservation data."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: str
    room_id: Optional[str]
    user_id: str
    scheduled_at: datetime
    work_duration: int
    break_duration: int
    description: Optional[str]
    is_active: bool
    is_completed: bool
    recurrence_type: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    notification_minutes: int = 5
    notification_sent: bool = False
    created_at: datetime
    updated_at: datetime

