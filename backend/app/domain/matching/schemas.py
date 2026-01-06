"""Pydantic schemas for matching pool."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class MatchingPoolCreate(BaseModel):
    """Schema for creating matching pool."""

    member_ids: List[str] = Field(..., min_length=2, max_length=8)
    preferred_match_type: str = Field(..., pattern="^(any|same_department|major_category)$")
    preferred_categories: List[str] | None = None
    matching_type: str = Field(..., pattern="^(blind|open)$")
    message: Optional[str] = Field(None, max_length=200)

    @field_validator("member_ids")
    @classmethod
    def validate_member_ids(cls, v: List[str]) -> List[str]:
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
    member_ids: List[str]
    department: str
    grade: str
    gender: str
    preferred_match_type: str
    preferred_categories: List[str] | None
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
    total_all: int
    total_matched: int
    total_expired: int
    by_status: Dict[str, int]
    by_member_count: Dict[str, int]
    by_gender: Dict[str, int]
    by_department: Dict[str, int]
    by_matching_type: Dict[str, int]
    average_wait_time_hours: float


class MatchingProposalStats(BaseModel):
    """Schema for matching proposal statistics."""

    total_proposals: int
    by_status: Dict[str, int]
    matched_count: int
    success_rate: float
    acceptance_rate: float
    rejection_rate: float
    pending_count: int
    average_matching_time_hours: float
    min_matching_time_hours: float
    max_matching_time_hours: float
    daily_matches: List[Dict[str, Any]]
    weekly_matches: List[Dict[str, Any]]
    monthly_matches: List[Dict[str, Any]]


class ComprehensiveMatchingStats(BaseModel):
    """Comprehensive matching statistics combining pools and proposals."""

    pools: MatchingPoolStats
    proposals: MatchingProposalStats
