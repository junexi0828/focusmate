"""User settings repository."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.user_settings import UserSettings


class UserSettingsRepository:
    """Repository for user settings operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository."""
        self.db = db

    async def create(self, settings: UserSettings) -> UserSettings:
        """Create new user settings.

        Args:
            settings: User settings to create

        Returns:
            Created user settings
        """
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def get_by_user_id(self, user_id: str) -> Optional[UserSettings]:
        """Get user settings by user ID.

        Args:
            user_id: User identifier

        Returns:
            User settings if found, None otherwise
        """
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, settings_id: str) -> Optional[UserSettings]:
        """Get user settings by ID.

        Args:
            settings_id: Settings identifier

        Returns:
            User settings if found, None otherwise
        """
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.id == settings_id)
        )
        return result.scalar_one_or_none()

    async def update(self, settings: UserSettings) -> UserSettings:
        """Update user settings.

        Args:
            settings: User settings to update

        Returns:
            Updated user settings
        """
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def delete(self, settings: UserSettings) -> None:
        """Delete user settings.

        Args:
            settings: User settings to delete
        """
        await self.db.delete(settings)
        await self.db.commit()
