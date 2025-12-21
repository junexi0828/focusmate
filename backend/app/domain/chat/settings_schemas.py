"""Chat room settings schema and endpoints."""


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

    notifications_enabled: bool | None = None
    mention_notifications: bool | None = None
    allow_invites: bool | None = None
    require_approval: bool | None = None
    allow_reactions: bool | None = None
    allow_threads: bool | None = None
    allow_file_uploads: bool | None = None
    max_file_size_mb: int | None = None
    slow_mode_seconds: int | None = None
    link_preview_enabled: bool | None = None
