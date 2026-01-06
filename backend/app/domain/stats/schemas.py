from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserGoalCreate(BaseModel):
    """Schema for creating/updating user goals."""

    daily_goal_minutes: int = Field(ge=0, le=1440, description="Daily goal in minutes")
    weekly_goal_sessions: int = Field(ge=0, le=100, description="Weekly session goal")


class UserGoalResponse(BaseModel):
    """Schema for user goal response."""

    id: str
    user_id: str
    daily_goal_minutes: int
    weekly_goal_sessions: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ManualSessionCreate(BaseModel):
    """Schema for creating manual session.

    Note: session_type uses Literal for validation (focus or break only).
    """

    session_type: Literal["focus", "break"] = Field(
        ...,
        description="Session type: 'focus' for work sessions, 'break' for rest sessions"
    )
    duration_minutes: int = Field(
        ...,
        ge=1,
        le=480,
        description="Session duration in minutes (1-480)"
    )
    completed_at: datetime | None = Field(
        None,
        description="When the session was completed. Defaults to now if not provided."
    )


class ManualSessionResponse(BaseModel):
    """Schema for manual session response."""

    id: str
    user_id: str
    duration_minutes: int
    session_type: str
    completed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
