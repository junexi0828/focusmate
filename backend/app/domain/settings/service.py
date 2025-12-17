"""User settings domain service."""

from typing import Optional

from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.security import hash_password, verify_password
from app.domain.settings.schemas import (
    EmailChangeRequest,
    PasswordChangeRequest,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from app.infrastructure.database.models.user_settings import UserSettings
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.user_settings_repository import (
    UserSettingsRepository,
)
from app.shared.utils.uuid import generate_uuid


class UserSettingsService:
    """User settings service for managing user preferences and account settings."""

    def __init__(
        self,
        settings_repository: UserSettingsRepository,
        user_repository: UserRepository,
    ) -> None:
        """Initialize service."""
        self.settings_repository = settings_repository
        self.user_repository = user_repository

    async def get_settings(self, user_id: str) -> UserSettingsResponse:
        """Get user settings.

        Args:
            user_id: User identifier

        Returns:
            User settings

        Raises:
            UnauthorizedException: If settings not found
        """
        settings = await self.settings_repository.get_by_user_id(user_id)

        # Create default settings if not found
        if not settings:
            settings = await self._create_default_settings(user_id)

        return UserSettingsResponse.model_validate(settings)

    async def update_settings(
        self, user_id: str, data: UserSettingsUpdate
    ) -> UserSettingsResponse:
        """Update user settings.

        Args:
            user_id: User identifier
            data: Settings update data

        Returns:
            Updated user settings

        Raises:
            UnauthorizedException: If settings not found
        """
        settings = await self.settings_repository.get_by_user_id(user_id)

        # Create default settings if not found
        if not settings:
            settings = await self._create_default_settings(user_id)

        # Update fields
        if data.theme is not None:
            settings.theme = data.theme
        if data.language is not None:
            settings.language = data.language
        if data.notification_email is not None:
            settings.notification_email = data.notification_email
        if data.notification_push is not None:
            settings.notification_push = data.notification_push
        if data.notification_session is not None:
            settings.notification_session = data.notification_session
        if data.notification_achievement is not None:
            settings.notification_achievement = data.notification_achievement
        if data.notification_message is not None:
            settings.notification_message = data.notification_message
        if data.do_not_disturb_start is not None:
            settings.do_not_disturb_start = data.do_not_disturb_start
        if data.do_not_disturb_end is not None:
            settings.do_not_disturb_end = data.do_not_disturb_end
        if data.session_reminder is not None:
            settings.session_reminder = data.session_reminder
        if data.custom_settings is not None:
            settings.custom_settings = data.custom_settings

        updated_settings = await self.settings_repository.update(settings)
        return UserSettingsResponse.model_validate(updated_settings)

    async def change_password(
        self, user_id: str, data: PasswordChangeRequest
    ) -> bool:
        """Change user password.

        Args:
            user_id: User identifier
            data: Password change data

        Returns:
            True if password changed successfully

        Raises:
            UnauthorizedException: If current password is incorrect
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        # Verify current password
        if not verify_password(data.current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")

        # Update password
        user.hashed_password = hash_password(data.new_password)
        await self.user_repository.update(user)
        return True

    async def change_email(self, user_id: str, data: EmailChangeRequest) -> bool:
        """Change user email.

        Args:
            user_id: User identifier
            data: Email change data

        Returns:
            True if email changed successfully

        Raises:
            UnauthorizedException: If password is incorrect
            ValidationException: If email already exists
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Password is incorrect")

        # Check if email already exists
        existing_user = await self.user_repository.get_by_email(data.new_email)
        if existing_user and existing_user.id != user_id:
            raise ValidationException("email", "Email already in use")

        # Update email
        user.email = data.new_email
        user.is_verified = False  # Reset verification status
        await self.user_repository.update(user)
        return True

    async def _create_default_settings(self, user_id: str) -> UserSettings:
        """Create default settings for a user.

        Args:
            user_id: User identifier

        Returns:
            Created default settings
        """
        settings = UserSettings(
            id=generate_uuid(),
            user_id=user_id,
            theme="system",
            language="ko",
            notification_email=True,
            notification_push=True,
            notification_session=True,
            notification_achievement=True,
            notification_message=True,
            session_reminder=True,
        )
        return await self.settings_repository.create(settings)
