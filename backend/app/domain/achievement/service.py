"""Achievement domain service - gamification and achievement tracking."""

from datetime import datetime, timedelta, timezone

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
from app.infrastructure.repositories.community_repository import PostRepository
from app.infrastructure.repositories.session_history_repository import SessionHistoryRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.shared.utils.uuid import generate_uuid


class AchievementService:
    """Achievement and gamification service."""

    def __init__(
        self,
        achievement_repo: AchievementRepository,
        user_achievement_repo: UserAchievementRepository,
        user_repo: UserRepository,
        post_repo: PostRepository | None = None,
        session_repo: SessionHistoryRepository | None = None,
    ) -> None:
        self.achievement_repo = achievement_repo
        self.user_achievement_repo = user_achievement_repo
        self.user_repo = user_repo
        self.post_repo = post_repo
        self.session_repo = session_repo

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
            current_progress = await self._calculate_progress(
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
            current_progress = await self._calculate_progress(
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

    async def _calculate_progress(self, user, requirement_type: str) -> int:
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
            return await self._calculate_streak_days(user.id)
        elif requirement_type == "community_posts":
            # Get community post count from repository
            return await self._get_community_post_count(user.id)
        else:
            return 0

    async def _get_community_post_count(self, user_id: str) -> int:
        """Get total community posts count for a user.

        Args:
            user_id: User identifier

        Returns:
            Total number of community posts
        """
        if not self.post_repo:
            return 0
        return await self.post_repo.get_count_by_user(user_id)

    async def _calculate_streak_days(self, user_id: str) -> int:
        """Calculate consecutive days streak from session history.

        Args:
            user_id: User identifier

        Returns:
            Number of consecutive days with sessions
        """
        if not self.session_repo:
            return 0

        # Get sessions from the last 365 days
        since = datetime.now(timezone.utc) - timedelta(days=365)
        sessions = await self.session_repo.get_by_user_since(user_id, since)

        if not sessions:
            return 0

        # Extract unique dates (normalize to date only, ignoring time)
        session_dates = set()
        for session in sessions:
            # Convert to date (timezone-aware)
            if session.completed_at:
                date = session.completed_at.date()
                session_dates.add(date)

        if not session_dates:
            return 0

        # Sort dates in descending order
        sorted_dates = sorted(session_dates, reverse=True)

        # Calculate streak from today backwards
        today = datetime.now(timezone.utc).date()
        streak = 0
        current_date = today

        # Check if today has a session
        if sorted_dates and sorted_dates[0] == today:
            streak = 1
            current_date = today - timedelta(days=1)
        elif sorted_dates and sorted_dates[0] == today - timedelta(days=1):
            # Yesterday has a session, but not today - streak starts from yesterday
            streak = 1
            current_date = sorted_dates[0] - timedelta(days=1)
        else:
            # No recent sessions
            return 0

        # Count consecutive days backwards
        for date in sorted_dates[1:]:
            if date == current_date:
                streak += 1
                current_date = date - timedelta(days=1)
            else:
                # Gap found, streak is broken
                break

        return streak
