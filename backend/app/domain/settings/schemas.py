"""User settings domain schemas."""


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
    do_not_disturb_start: str | None = None
    do_not_disturb_end: str | None = None
    session_reminder: bool
    custom_settings: dict | None = None


class UserSettingsUpdate(BaseModel):
    """User settings update request."""

    model_config = ConfigDict(strict=True)

    theme: str | None = Field(None, pattern="^(light|dark|system)$")
    language: str | None = Field(None, min_length=2, max_length=10)
    notification_email: bool | None = None
    notification_push: bool | None = None
    notification_session: bool | None = None
    notification_achievement: bool | None = None
    notification_message: bool | None = None
    do_not_disturb_start: str | None = Field(None, pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    do_not_disturb_end: str | None = Field(None, pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    session_reminder: bool | None = None
    custom_settings: dict | None = None


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
