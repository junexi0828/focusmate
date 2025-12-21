"""Achievement domain schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AchievementBase(BaseModel):
    """Base achievement schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    icon: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., pattern="^(sessions|time|streak|social)$")
    requirement_type: str = Field(..., pattern="^(total_sessions|total_focus_time|streak_days|community_posts)$")
    requirement_value: int = Field(..., gt=0)
    points: int = Field(default=10, ge=0)


class AchievementCreate(AchievementBase):
    """Schema for creating a new achievement."""



class AchievementResponse(AchievementBase):
    """Achievement response schema."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserAchievementResponse(BaseModel):
    """User achievement unlock response."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: str
    user_id: str
    achievement_id: str
    unlocked_at: datetime
    progress: int
    achievement: AchievementResponse | None = None


class AchievementUnlockRequest(BaseModel):
    """Request to check and unlock achievements for a user."""

    user_id: str = Field(..., min_length=1, max_length=36)


class AchievementProgressResponse(BaseModel):
    """Achievement progress for a specific user."""

    achievement: AchievementResponse
    is_unlocked: bool
    progress: int
    progress_percentage: float
    unlocked_at: datetime | None = None
