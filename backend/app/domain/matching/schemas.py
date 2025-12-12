"""Pydantic schemas for matching pool."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class MatchingPoolCreate(BaseModel):
    """Schema for creating matching pool."""

    member_ids: list[str] = Field(..., min_length=2, max_length=8)
    preferred_match_type: str = Field(..., pattern="^(any|same_department|major_category)$")
    preferred_categories: Optional[list[str]] = None
    matching_type: str = Field(..., pattern="^(blind|open)$")
    message: Optional[str] = Field(None, max_length=200)

    @field_validator("member_ids")
    @classmethod
    def validate_member_ids(cls, v: list[str]) -> list[str]:
        if len(v) < 2 or len(v) > 8:
            raise ValueError("Member count must be between 2 and 8")
        if len(set(v)) != len(v):
            raise ValueError("Duplicate member IDs not allowed")
        return v


class MatchingPoolResponse(BaseModel):
    """Schema for matching pool response."""

    pool_id: UUID
    creator_id: str
    member_count: int
    member_ids: list[str]
    department: str
    grade: str
    gender: str
    preferred_match_type: str
    preferred_categories: Optional[list[str]]
    matching_type: str
    message: Optional[str]
    status: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class MatchingPoolStats(BaseModel):
    """Schema for matching pool statistics."""

    total_waiting: int
    by_member_count: dict[str, int]
    by_gender: dict[str, int]
    average_wait_time_hours: float
