"""User stats schemas."""

from datetime import datetime
from typing import Optional

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
    """Schema for creating manual session."""

    duration_minutes: int = Field(ge=1, le=480, description="Session duration in minutes")
    session_type: str = Field(pattern="^(focus|break)$", description="Session type")
    completed_at: datetime = Field(description="When the session was completed")


class ManualSessionResponse(BaseModel):
    """Schema for manual session response."""

    id: str
    user_id: str
    duration_minutes: int
    session_type: str
    completed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
