"""User domain schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """User registration request."""

    model_config = ConfigDict(strict=True)

    email: EmailStr
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login request."""

    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response (without password)."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    is_admin: bool = False
    bio: str | None
    school: str | None = None
    profile_image: str | None = None
    total_focus_time: int
    total_sessions: int
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    """User profile update request."""

    model_config = ConfigDict(strict=True)

    username: str | None = Field(None, min_length=2, max_length=50)
    bio: str | None = Field(None, max_length=500)
    school: str | None = Field(None, max_length=100)
    profile_image: str | None = Field(None, max_length=500)


class TokenResponse(BaseModel):
    """JWT token response."""

    model_config = ConfigDict(strict=True)

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetRequest(BaseModel):
    """Password reset request."""

    model_config = ConfigDict(strict=True)

    email: EmailStr


class PasswordResetVerify(BaseModel):
    """Password reset token verification."""

    model_config = ConfigDict(strict=True)

    token: str


class PasswordResetComplete(BaseModel):
    """Password reset completion."""

    model_config = ConfigDict(strict=True)

    token: str
    new_password: str = Field(min_length=8, max_length=100)


class NaverOAuthCallback(BaseModel):
    """Naver OAuth callback data."""

    model_config = ConfigDict(strict=True)

    code: str
    state: str | None = None
