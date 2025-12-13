"""Unit tests for ranking service."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from app.domain.ranking.service import RankingService
from app.infrastructure.repositories.ranking_repository import RankingRepository


@pytest.fixture
def mock_ranking_repository():
    """Create mock ranking repository."""
    return AsyncMock(spec=RankingRepository)


@pytest.fixture
def ranking_service(mock_ranking_repository):
    """Create ranking service with mocked dependencies."""
    return RankingService(repository=mock_ranking_repository)


class TestRankingService:
    """Test cases for RankingService."""

    @pytest.mark.asyncio
    async def test_get_top_users(self, ranking_service, mock_ranking_repository):
        """Test getting top ranked users."""
        expected_rankings = [
            {"user_id": str(uuid4()), "username": "user1", "score": 1000, "rank": 1},
            {"user_id": str(uuid4()), "username": "user2", "score": 900, "rank": 2},
            {"user_id": str(uuid4()), "username": "user3", "score": 800, "rank": 3},
        ]

        mock_ranking_repository.get_top_users.return_value = expected_rankings

        result = await ranking_service.get_top_users(limit=3)

        assert len(result) == 3
        assert result[0]["rank"] == 1
        assert result[0]["score"] > result[1]["score"]
        mock_ranking_repository.get_top_users.assert_called_once_with(limit=3)

    @pytest.mark.asyncio
    async def test_get_user_rank(self, ranking_service, mock_ranking_repository):
        """Test getting user's rank."""
        user_id = str(uuid4())
        expected_rank = {
            "user_id": user_id,
            "score": 750,
            "rank": 5,
        }

        mock_ranking_repository.get_user_rank.return_value = expected_rank

        result = await ranking_service.get_user_rank(user_id)

        assert result["user_id"] == user_id
        assert result["rank"] == 5
        mock_ranking_repository.get_user_rank.assert_called_once_with(user_id)


def test_ranking_service_import():
    """Test that ranking service can be imported."""
    from app.domain.ranking.service import RankingService
    assert RankingService is not None
