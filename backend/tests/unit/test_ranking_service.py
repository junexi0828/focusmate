"""Unit tests for ranking service."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.ranking.service import RankingService


@pytest.fixture
def mock_ranking_repository():
    """Create mock ranking repository."""
    return AsyncMock()


@pytest.fixture
def ranking_service(mock_ranking_repository):
    """Create ranking service with mocked dependencies."""
    return RankingService(repository=mock_ranking_repository)


class TestRankingService:
    """Test cases for RankingService."""

    @pytest.mark.asyncio
    async def test_get_hall_of_fame(self, ranking_service, mock_ranking_repository):
        """Test getting hall of fame data."""
        expected_hall_of_fame = {
            "period": "all",
            "total_teams": 3,
            "teams": [
                {"team_id": uuid4(), "team_name": "Team 1", "total_focus_time": 1000, "total_game_score": 500},
                {"team_id": uuid4(), "team_name": "Team 2", "total_focus_time": 800, "total_game_score": 400},
                {"team_id": uuid4(), "team_name": "Team 3", "total_focus_time": 600, "total_game_score": 300},
            ],
            "top_focus_teams": [],
            "top_game_teams": []
        }

        mock_ranking_repository.get_comprehensive_leaderboard.return_value = expected_hall_of_fame["teams"]

        result = await ranking_service.get_hall_of_fame(period="all")

        assert result["total_teams"] == 3
        assert result["teams"][0]["total_focus_time"] == 1000
        mock_ranking_repository.get_comprehensive_leaderboard.assert_called_once_with("all")

    @pytest.mark.asyncio
    async def test_get_team_statistics(self, ranking_service, mock_ranking_repository):
        """Test getting team statistics."""
        team_id = uuid4()
        expected_stats = {
            "total_focus_time": 1200,
            "total_sessions": 15
        }
        mock_members = [AsyncMock(), AsyncMock()]
        mock_sessions = []

        mock_ranking_repository.get_team_stats.return_value = expected_stats
        mock_ranking_repository.get_team_members.return_value = mock_members
        mock_ranking_repository.get_team_sessions.return_value = mock_sessions

        result = await ranking_service.get_team_statistics(team_id)

        assert result["team_id"] == team_id
        assert result["total_focus_time"] == 1200
        assert result["member_count"] == 2
        mock_ranking_repository.get_team_stats.assert_called_once_with(team_id)


def test_ranking_service_import():
    """Test that ranking service can be imported."""
    from app.domain.ranking.service import RankingService
    assert RankingService is not None
