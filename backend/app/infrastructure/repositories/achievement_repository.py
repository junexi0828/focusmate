"""Achievement repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.achievement import Achievement, UserAchievement


class AchievementRepository:
    """Repository for achievement data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, achievement: Achievement) -> Achievement:
        """Create achievement."""
        self.db.add(achievement)
        await self.db.flush()
        await self.db.refresh(achievement)
        return achievement

    async def get_by_id(self, achievement_id: str) -> Achievement | None:
        """Get achievement by ID."""
        result = await self.db.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Achievement | None:
        """Get achievement by name."""
        result = await self.db.execute(
            select(Achievement).where(Achievement.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Achievement]:
        """Get all active achievements."""
        result = await self.db.execute(
            select(Achievement).where(Achievement.is_active == True).order_by(Achievement.category, Achievement.requirement_value)
        )
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> list[Achievement]:
        """Get achievements by category."""
        result = await self.db.execute(
            select(Achievement)
            .where(Achievement.category == category)
            .where(Achievement.is_active == True)
            .order_by(Achievement.requirement_value)
        )
        return list(result.scalars().all())

    async def update(self, achievement: Achievement) -> Achievement:
        """Update achievement."""
        await self.db.flush()
        await self.db.refresh(achievement)
        return achievement


class UserAchievementRepository:
    """Repository for user achievement data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, user_achievement: UserAchievement) -> UserAchievement:
        """Create user achievement unlock record."""
        self.db.add(user_achievement)
        await self.db.flush()
        await self.db.refresh(user_achievement)
        return user_achievement

    async def get_by_user_and_achievement(
        self, user_id: str, achievement_id: str
    ) -> UserAchievement | None:
        """Get user achievement by user and achievement ID."""
        result = await self.db.execute(
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .where(UserAchievement.achievement_id == achievement_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: str) -> list[UserAchievement]:
        """Get all achievements for a user."""
        result = await self.db.execute(
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.unlocked_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, user_achievement: UserAchievement) -> UserAchievement:
        """Update user achievement progress."""
        await self.db.flush()
        await self.db.refresh(user_achievement)
        return user_achievement
