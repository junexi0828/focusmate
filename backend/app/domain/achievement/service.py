"""Achievement domain service - gamification and achievement tracking."""

from datetime import datetime, timezone

from app.core.exceptions import ValidationException
from app.domain.achievement.schemas import (
    AchievementCreate,
    AchievementProgressResponse,
    AchievementResponse,
    UserAchievementResponse,
)
from app.infrastructure.database.models.achievement import Achievement, UserAchievement
from app.infrastructure.repositories.achievement_repository import (
    AchievementRepository,
    UserAchievementRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository
from app.shared.utils.uuid import generate_uuid


class AchievementService:
    """Achievement and gamification service."""

    def __init__(
        self,
        achievement_repo: AchievementRepository,
        user_achievement_repo: UserAchievementRepository,
        user_repo: UserRepository,
    ) -> None:
        self.achievement_repo = achievement_repo
        self.user_achievement_repo = user_achievement_repo
        self.user_repo = user_repo

    async def create_achievement(self, data: AchievementCreate) -> AchievementResponse:
        """Create a new achievement definition.

        Args:
            data: Achievement details

        Returns:
            Created achievement

        Raises:
            ValidationException: If achievement name already exists
        """
        # Check if name already exists
        existing = await self.achievement_repo.get_by_name(data.name)
        if existing:
            raise ValidationException("name", f"Achievement '{data.name}' already exists")

        achievement = Achievement(
            id=generate_uuid(),
            name=data.name,
            description=data.description,
            icon=data.icon,
            category=data.category,
            requirement_type=data.requirement_type,
            requirement_value=data.requirement_value,
            points=data.points,
            is_active=True,
        )

        created = await self.achievement_repo.create(achievement)
        return AchievementResponse.model_validate(created)

    async def get_all_achievements(self) -> list[AchievementResponse]:
        """Get all active achievements."""
        achievements = await self.achievement_repo.get_all_active()
        return [AchievementResponse.model_validate(a) for a in achievements]

    async def get_achievements_by_category(self, category: str) -> list[AchievementResponse]:
        """Get achievements by category."""
        achievements = await self.achievement_repo.get_by_category(category)
        return [AchievementResponse.model_validate(a) for a in achievements]

    async def get_user_achievements(self, user_id: str) -> list[UserAchievementResponse]:
        """Get all unlocked achievements for a user."""
        user_achievements = await self.user_achievement_repo.get_all_by_user(user_id)

        result = []
        for ua in user_achievements:
            achievement = await self.achievement_repo.get_by_id(ua.achievement_id)
            response = UserAchievementResponse.model_validate(ua)
            if achievement:
                response.achievement = AchievementResponse.model_validate(achievement)
            result.append(response)

        return result

    async def get_user_achievement_progress(self, user_id: str) -> list[AchievementProgressResponse]:
        """Get achievement progress for a user across all achievements.

        Args:
            user_id: User identifier

        Returns:
            List of achievement progress including unlocked status
        """
        # Get user stats
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return []

        # Get all active achievements
        all_achievements = await self.achievement_repo.get_all_active()

        # Get user's unlocked achievements
        user_achievements = await self.user_achievement_repo.get_all_by_user(user_id)
        unlocked_map = {ua.achievement_id: ua for ua in user_achievements}

        result = []
        for achievement in all_achievements:
            # Calculate progress based on requirement type
            current_progress = self._calculate_progress(
                user, achievement.requirement_type
            )

            is_unlocked = achievement.id in unlocked_map
            progress_percentage = min(
                100.0, (current_progress / achievement.requirement_value) * 100
            )

            progress_response = AchievementProgressResponse(
                achievement=AchievementResponse.model_validate(achievement),
                is_unlocked=is_unlocked,
                progress=current_progress,
                progress_percentage=progress_percentage,
                unlocked_at=unlocked_map[achievement.id].unlocked_at if is_unlocked else None,
            )
            result.append(progress_response)

        return result

    async def check_and_unlock_achievements(self, user_id: str) -> list[UserAchievementResponse]:
        """Check user progress and unlock any newly achieved achievements.

        Args:
            user_id: User identifier

        Returns:
            List of newly unlocked achievements
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return []

        # Get all active achievements
        all_achievements = await self.achievement_repo.get_all_active()

        # Get already unlocked achievements
        user_achievements = await self.user_achievement_repo.get_all_by_user(user_id)
        unlocked_ids = {ua.achievement_id for ua in user_achievements}

        newly_unlocked = []
        for achievement in all_achievements:
            # Skip if already unlocked
            if achievement.id in unlocked_ids:
                continue

            # Calculate current progress
            current_progress = self._calculate_progress(
                user, achievement.requirement_type
            )

            # Check if requirement is met
            if current_progress >= achievement.requirement_value:
                # Unlock achievement
                user_achievement = UserAchievement(
                    id=generate_uuid(),
                    user_id=user_id,
                    achievement_id=achievement.id,
                    unlocked_at=datetime.now(timezone.utc),
                    progress=current_progress,
                )
                created = await self.user_achievement_repo.create(user_achievement)

                response = UserAchievementResponse.model_validate(created)
                response.achievement = AchievementResponse.model_validate(achievement)
                newly_unlocked.append(response)

        return newly_unlocked

    def _calculate_progress(self, user, requirement_type: str) -> int:
        """Calculate user's progress for a specific requirement type.

        Args:
            user: User model instance
            requirement_type: Type of requirement to check

        Returns:
            Current progress value
        """
        if requirement_type == "total_sessions":
            return user.total_sessions
        elif requirement_type == "total_focus_time":
            return user.total_focus_time
        elif requirement_type == "streak_days":
            # Calculate consecutive days streak from session history
            return self._calculate_streak_days(user.id)
        elif requirement_type == "community_posts":
            # Get community post count from repository
            return self._get_community_post_count(user.id)
        else:
            return 0

    def _get_community_post_count(self, user_id: str) -> int:
        """Get total community posts count for a user.

        Args:
            user_id: User identifier

        Returns:
            Total number of community posts
        """
        # This would integrate with CommunityRepository
        # For now, return 0 as placeholder until repository is available
        # TODO: Integrate with CommunityRepository

        # Pseudo-logic for when repository is available:
        # 1. Query community posts table by user_id
        # 2. Count total posts
        # 3. Return count

        return 0  # Placeholder until CommunityRepository integration

    def _calculate_streak_days(self, user_id: str) -> int:
        """Calculate consecutive days streak from session history.

        Args:
            user_id: User identifier

        Returns:
            Number of consecutive days with sessions
        """
        from datetime import datetime, timedelta

        # Get recent sessions (last 365 days)
        # This would need SessionRepository integration
        # For now, return 0 as placeholder until repository is available
        # TODO: Integrate with SessionRepository to get actual session dates

        # Pseudo-logic for when repository is available:
        # 1. Get all sessions ordered by completed_at DESC
        # 2. Extract unique dates
        # 3. Count consecutive days from today backwards
        # 4. Break on first gap

        return 0  # Placeholder until SessionRepository integration
