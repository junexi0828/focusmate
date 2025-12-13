"""Chat room settings schema and endpoints."""

from typing import Optional

from pydantic import BaseModel


class ChatRoomSettings(BaseModel):
    """Chat room settings."""

    # Notifications
    notifications_enabled: bool = True
    mention_notifications: bool = True

    # Privacy
    allow_invites: bool = True
    require_approval: bool = False

    # Messages
    allow_reactions: bool = True
    allow_threads: bool = True
    allow_file_uploads: bool = True
    max_file_size_mb: int = 50

    # Moderation
    slow_mode_seconds: int = 0
    link_preview_enabled: bool = True


class ChatRoomSettingsUpdate(BaseModel):
    """Update chat room settings."""

    notifications_enabled: Optional[bool] = None
    mention_notifications: Optional[bool] = None
    allow_invites: Optional[bool] = None
    require_approval: Optional[bool] = None
    allow_reactions: Optional[bool] = None
    allow_threads: Optional[bool] = None
    allow_file_uploads: Optional[bool] = None
    max_file_size_mb: Optional[int] = None
    slow_mode_seconds: Optional[int] = None
    link_preview_enabled: Optional[bool] = None
