"""Unit tests for matching service."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.domain.matching.service import MatchingService
from app.domain.matching.schemas import MatchingPoolCreate, MatchingPreferences
from app.infrastructure.repositories.matching_pool_repository import MatchingPoolRepository


@pytest.fixture
def mock_pool_repository():
    """Create mock matching pool repository."""
    return AsyncMock(spec=MatchingPoolRepository)


@pytest.fixture
def matching_service(mock_pool_repository):
    """Create matching service with mocked dependencies."""
    return MatchingService(pool_repository=mock_pool_repository)


class TestMatchingService:
    """Test cases for MatchingService."""

    @pytest.mark.asyncio
    async def test_create_matching_pool(self, matching_service, mock_pool_repository):
        """Test creating a matching pool."""
        pool_data = MatchingPoolCreate(
            pool_type="skill_based",
            max_participants=4,
            scheduled_start=datetime.utcnow() + timedelta(hours=1),
        )

        expected_pool = {
            "id": str(uuid4()),
            "pool_type": "skill_based",
            "max_participants": 4,
            "current_participants": 0,
        }

        mock_pool_repository.create.return_value = expected_pool

        result = await matching_service.create_pool(pool_data)

        assert result is not None
        assert result["pool_type"] == "skill_based"
        mock_pool_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_matching_pools(self, matching_service, mock_pool_repository):
        """Test finding available matching pools."""
        preferences = MatchingPreferences(
            preferred_pool_type="skill_based",
            max_distance=10,
        )

        expected_pools = [
            {"id": str(uuid4()), "pool_type": "skill_based", "current_participants": 2},
            {"id": str(uuid4()), "pool_type": "skill_based", "current_participants": 1},
        ]

        mock_pool_repository.find_available.return_value = expected_pools

        result = await matching_service.find_pools(preferences)

        assert len(result) == 2
        assert all(pool["pool_type"] == "skill_based" for pool in result)


def test_matching_service_import():
    """Test that matching service can be imported."""
    from app.domain.matching.service import MatchingService
    assert MatchingService is not None
