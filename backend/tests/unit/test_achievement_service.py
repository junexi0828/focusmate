"""Unit tests for achievement service."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from app.domain.achievement.service import AchievementService
from app.infrastructure.repositories.achievement_repository import AchievementRepository
from app.infrastructure.repositories.user_repository import UserRepository


@pytest.fixture
def mock_achievement_repository():
    """Create mock achievement repository."""
    return AsyncMock(spec=AchievementRepository)


@pytest.fixture
def mock_user_repository():
    """Create mock user repository."""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def achievement_service(mock_achievement_repository, mock_user_repository):
    """Create achievement service with mocked dependencies."""
    return AchievementService(
        achievement_repository=mock_achievement_repository,
        user_repository=mock_user_repository,
    )


class TestAchievementService:
    """Test cases for AchievementService."""

    @pytest.mark.asyncio
    async def test_get_user_achievements(self, achievement_service, mock_achievement_repository):
        """Test getting user achievements."""
        user_id = str(uuid4())
        expected_achievements = [
            {
                "id": str(uuid4()),
                "name": "First Session",
                "description": "Complete your first session",
                "unlocked": True,
            },
            {
                "id": str(uuid4()),
                "name": "Marathon Runner",
                "description": "Complete 10 sessions",
                "unlocked": False,
            },
        ]

        mock_achievement_repository.get_user_achievements.return_value = expected_achievements

        result = await achievement_service.get_user_achievements(user_id)

        assert len(result) == 2
        assert result[0]["unlocked"] is True
        mock_achievement_repository.get_user_achievements.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_unlock_achievement(self, achievement_service, mock_achievement_repository):
        """Test unlocking an achievement."""
        user_id = str(uuid4())
        achievement_id = str(uuid4())

        expected_result = {
            "id": achievement_id,
            "user_id": user_id,
            "unlocked_at": "2025-12-13T00:00:00",
        }

        mock_achievement_repository.unlock.return_value = expected_result

        result = await achievement_service.unlock_achievement(user_id, achievement_id)

        assert result["user_id"] == user_id
        assert result["id"] == achievement_id


def test_achievement_service_import():
    """Test that achievement service can be imported."""
    from app.domain.achievement.service import AchievementService
    assert AchievementService is not None
