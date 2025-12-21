"""User Settings ORM Model."""

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class UserSettings(Base, TimestampMixin):
    """User settings model for managing user preferences.

    Attributes:
        id: Unique settings identifier (UUID)
        user_id: Associated user ID
        theme: UI theme preference (light, dark, system)
        language: Language preference
        notification_email: Email notification enabled
        notification_push: Push notification enabled
        notification_session: Session notification enabled
        notification_achievement: Achievement notification enabled
        notification_message: Message notification enabled
        do_not_disturb_start: Do not disturb start time (HH:MM)
        do_not_disturb_end: Do not disturb end time (HH:MM)
        session_reminder: Session reminder enabled
        custom_settings: Additional custom settings (JSON)
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Unique settings identifier (UUID)",
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="Associated user ID",
    )

    # Theme settings
    theme: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="system",
        comment="UI theme (light, dark, system)",
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="ko",
        comment="Language preference",
    )

    # Notification settings
    notification_email: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Email notification enabled",
    )

    notification_push: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Push notification enabled",
    )

    notification_session: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Session notification enabled",
    )

    notification_achievement: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Achievement notification enabled",
    )

    notification_message: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Message notification enabled",
    )

    # Do not disturb settings
    do_not_disturb_start: Mapped[str | None] = mapped_column(
        String(5),
        nullable=True,
        comment="Do not disturb start time (HH:MM)",
    )

    do_not_disturb_end: Mapped[str | None] = mapped_column(
        String(5),
        nullable=True,
        comment="Do not disturb end time (HH:MM)",
    )

    # Session settings
    session_reminder: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Session reminder enabled",
    )

    # Custom settings (JSON)
    custom_settings: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional custom settings",
    )

    def __repr__(self) -> str:
        """String representation of UserSettings."""
        return f"<UserSettings(id={self.id}, user_id={self.user_id}, theme={self.theme})>"
