"""Unit tests for achievement service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.domain.achievement.service import AchievementService
from app.infrastructure.database.models.achievement import Achievement, UserAchievement


@pytest.fixture
def mock_achievement_repository():
    """Create mock achievement repository."""
    return AsyncMock()


@pytest.fixture
def mock_user_achievement_repository():
    """Create mock user achievement repository."""
    return AsyncMock()


@pytest.fixture
def mock_user_repository():
    """Create mock user repository."""
    return AsyncMock()


@pytest.fixture
def achievement_service(mock_achievement_repository, mock_user_achievement_repository, mock_user_repository):
    """Create achievement service with mocked dependencies."""
    return AchievementService(
        achievement_repo=mock_achievement_repository,
        user_achievement_repo=mock_user_achievement_repository,
        user_repo=mock_user_repository,
    )


class TestAchievementService:
    """Test cases for AchievementService."""

    @pytest.mark.asyncio
    async def test_get_user_achievements(
        self, achievement_service, mock_user_achievement_repository, mock_achievement_repository
    ):
        """Test getting user achievements."""
        user_id = str(uuid4())
        achievement_id = str(uuid4())

        mock_ua = UserAchievement(
            id=str(uuid4()),
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=datetime.now(UTC),
            progress=100
        )

        mock_achievement = Achievement(
            id=achievement_id,
            name="First Session",
            description="Complete your first session",
            icon="test-icon",
            category="sessions",
            requirement_type="total_sessions",
            requirement_value=1,
            points=10,
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )

        mock_user_achievement_repository.get_all_by_user.return_value = [mock_ua]
        mock_achievement_repository.get_by_id.return_value = mock_achievement

        result = await achievement_service.get_user_achievements(user_id)

        assert len(result) == 1
        assert result[0].achievement_id == achievement_id
        assert result[0].achievement.name == "First Session"
        mock_user_achievement_repository.get_all_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_check_and_unlock_achievements(
        self, achievement_service, mock_achievement_repository, mock_user_achievement_repository, mock_user_repository
    ):
        """Test checking and unlocking achievements."""
        user_id = str(uuid4())

        # Mock user
        mock_user = Mock()
        mock_user.id = user_id
        mock_user.total_sessions = 5
        mock_user_repository.get_by_id.return_value = mock_user

        # Mock achievements to check
        achievement_id = str(uuid4())
        mock_achievement = Achievement(
            id=achievement_id,
            name="Fast Finisher",
            description="Complete 1 session",
            icon="icon",
            category="sessions",
            requirement_type="total_sessions",
            requirement_value=1,
            points=10,
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )

        mock_achievement_repository.get_all_active.return_value = [mock_achievement]
        mock_user_achievement_repository.get_all_by_user.return_value = []

        # Mock creation
        mock_created_ua = UserAchievement(
            id=str(uuid4()),
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=datetime.now(UTC),
            progress=5
        )
        mock_user_achievement_repository.create.return_value = mock_created_ua

        # Execute
        result = await achievement_service.check_and_unlock_achievements(user_id)

        assert len(result) == 1
        assert result[0].achievement_id == achievement_id
        mock_user_achievement_repository.create.assert_called_once()


def test_achievement_service_import():
    """Test that achievement service can be imported."""
    from app.domain.achievement.service import AchievementService
    assert AchievementService is not None
