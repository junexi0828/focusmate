"""Ranking domain schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Team Schemas
class TeamCreate(BaseModel):
    """Schema for creating a new team."""

    team_name: str = Field(..., min_length=2, max_length=100, description="Team name")
    team_type: str = Field(..., description="Team type: general, department, lab, club")
    mini_game_enabled: bool = Field(default=True, description="Enable mini-games")
    affiliation_info: dict | None = Field(None, description="School/department information")


class TeamUpdate(BaseModel):
    """Schema for updating team information."""

    team_name: str | None = Field(None, min_length=2, max_length=100)
    mini_game_enabled: bool | None = None


class TeamResponse(BaseModel):
    """Schema for team response."""

    team_id: UUID
    team_name: str
    team_type: str
    verification_status: str
    leader_id: str
    mini_game_enabled: bool
    invite_code: str | None
    affiliation_info: dict | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Team Member Schemas
class TeamMemberResponse(BaseModel):
    """Schema for team member response."""

    member_id: UUID
    team_id: UUID
    user_id: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


# Team Invitation Schemas
class TeamInvitationCreate(BaseModel):
    """Schema for creating a team invitation."""

    email: EmailStr = Field(..., description="Invitee email address")


class TeamInvitationResponse(BaseModel):
    """Schema for team invitation response."""

    invitation_id: UUID
    team_id: UUID
    email: str
    invited_by: str
    status: str
    created_at: datetime
    expires_at: datetime
    accepted_at: datetime | None

    class Config:
        from_attributes = True


# Session Schemas
class SessionCreate(BaseModel):
    """Schema for creating a ranking session."""

    team_id: UUID
    duration_minutes: int = Field(..., gt=0, description="Session duration in minutes")
    session_type: str = Field(..., description="Session type: work or break")


class SessionComplete(BaseModel):
    """Schema for completing a session."""

    actual_duration: int = Field(..., gt=0, description="Actual duration in minutes")
    success: bool = Field(default=True, description="Whether session was successful")


class SessionResponse(BaseModel):
    """Schema for session response."""

    session_id: UUID
    team_id: UUID
    user_id: str
    duration_minutes: int
    session_type: str
    success: bool
    completed_at: datetime

    class Config:
        from_attributes = True


# Mini-Game Schemas
class MiniGameStart(BaseModel):
    """Schema for starting a mini-game."""

    team_id: UUID
    game_type: str = Field(..., description="Game type: quiz, reaction, memory")


class MiniGameSubmit(BaseModel):
    """Schema for submitting mini-game result."""

    answer: str | None = None
    completion_time: float = Field(..., gt=0, description="Completion time in seconds")


class MiniGameResponse(BaseModel):
    """Schema for mini-game response."""

    game_id: UUID
    team_id: UUID
    user_id: str
    game_type: str
    score: int
    success: bool
    completion_time: float | None
    game_data: dict | None
    played_at: datetime

    class Config:
        from_attributes = True


# Verification Schemas
class VerificationRequestCreate(BaseModel):
    """Schema for creating a verification request."""

    team_id: UUID
    documents: list[dict] = Field(..., description="List of verification documents")
    team_member_list: list[dict] = Field(..., description="List of team members with details")


class VerificationRequestResponse(BaseModel):
    """Schema for verification request response."""

    request_id: UUID
    team_id: UUID
    documents: dict
    status: str
    admin_note: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
    reviewed_by: str | None

    class Config:
        from_attributes = True


# Leaderboard Schemas
class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry."""

    rank: int
    team_id: UUID
    team_name: str
    team_type: str
    score: float
    rank_change: int
    member_count: int | None = None
    average_score: float | None = None
    total_sessions: int | None = None  # Total number of sessions

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response."""

    ranking_type: str
    period: str
    updated_at: datetime
    leaderboard: list[LeaderboardEntry]


# Team Stats Schemas
class TeamStatsResponse(BaseModel):
    """Schema for team statistics."""

    team_id: UUID
    total_study_time: float
    total_sessions: int
    current_streak: int
    mini_game_score: int
    member_breakdown: list[dict] | None = None

    class Config:
        from_attributes = True
