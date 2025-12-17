"""User settings domain schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserSettingsResponse(BaseModel):
    """User settings response."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: str
    user_id: str
    theme: str
    language: str
    notification_email: bool
    notification_push: bool
    notification_session: bool
    notification_achievement: bool
    notification_message: bool
    do_not_disturb_start: Optional[str] = None
    do_not_disturb_end: Optional[str] = None
    session_reminder: bool
    custom_settings: Optional[dict] = None


class UserSettingsUpdate(BaseModel):
    """User settings update request."""

    model_config = ConfigDict(strict=True)

    theme: Optional[str] = Field(None, pattern="^(light|dark|system)$")
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_session: Optional[bool] = None
    notification_achievement: Optional[bool] = None
    notification_message: Optional[bool] = None
    do_not_disturb_start: Optional[str] = Field(None, pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    do_not_disturb_end: Optional[str] = Field(None, pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    session_reminder: Optional[bool] = None
    custom_settings: Optional[dict] = None


class PasswordChangeRequest(BaseModel):
    """Password change request."""

    model_config = ConfigDict(strict=True)

    current_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class EmailChangeRequest(BaseModel):
    """Email change request."""

    model_config = ConfigDict(strict=True)

    new_email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
