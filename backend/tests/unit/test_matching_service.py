"""Unit tests for matching service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.matching.schemas import MatchingPoolCreate, MatchingPoolResponse
from app.domain.matching.service import MatchingPoolService


@pytest.fixture
def mock_pool_repository():
    """Create mock matching pool repository."""
    return AsyncMock()


@pytest.fixture
def mock_verification_repository():
    """Create mock verification repository."""
    return AsyncMock()


@pytest.fixture
def matching_service(mock_pool_repository, mock_verification_repository):
    """Create matching service with mocked dependencies."""
    return MatchingPoolService(
        pool_repository=mock_pool_repository,
        verification_repository=mock_verification_repository,
    )


class TestMatchingService:
    """Test cases for MatchingPoolService."""

    @pytest.mark.asyncio
    async def test_create_matching_pool(
        self, matching_service, mock_pool_repository, mock_verification_repository
    ):
        """Test creating a matching pool."""
        creator_id = str(uuid4())
        member_id1 = creator_id
        member_id2 = str(uuid4())

        pool_data = MatchingPoolCreate(
            member_ids=[member_id1, member_id2],
            preferred_match_type="any",
            matching_type="open",
            message="Let's study together!",
        )

        # Mock verification data
        mock_verification = MagicMock()
        mock_verification.verification_status = "approved"
        mock_verification.department = "Computer Science"
        mock_verification.grade = "2"
        mock_verification.gender = "male"

        mock_verification_repository.get_verification_by_user.return_value = mock_verification
        mock_pool_repository.get_pool_by_creator.return_value = None
        mock_pool_repository.get_user_active_pool.return_value = None

        expected_pool = MatchingPoolResponse(
            pool_id=uuid4(),
            creator_id=creator_id,
            member_count=2,
            member_ids=[member_id1, member_id2],
            department="Computer Science",
            grade="2",
            gender="male",
            preferred_match_type="any",
            preferred_categories=[],
            matching_type="open",
            message="Let's study together!",
            status="waiting",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(hours=24)
        )

        mock_pool_repository.create_pool.return_value = expected_pool

        result = await matching_service.create_pool(creator_id, pool_data)

        assert result is not None
        assert str(result.creator_id) == creator_id
        assert result.member_count == 2
        mock_pool_repository.create_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_my_pool(self, matching_service, mock_pool_repository):
        """Test getting user's active pool."""
        user_id = str(uuid4())

        expected_pool = MatchingPoolResponse(
            pool_id=uuid4(),
            creator_id=user_id,
            member_count=2,
            member_ids=[user_id, str(uuid4())],
            department="Computer Science",
            grade="2",
            gender="male",
            preferred_match_type="any",
            preferred_categories=[],
            matching_type="open",
            message="Hello",
            status="waiting",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

        mock_pool_repository.get_user_active_pool.return_value = expected_pool

        result = await matching_service.get_my_pool(user_id)

        assert result is not None
        assert str(result.creator_id) == user_id
        mock_pool_repository.get_user_active_pool.assert_called_once_with(user_id)


def test_matching_service_import():
    """Test that matching service can be imported."""
    from app.domain.matching.service import MatchingPoolService
    assert MatchingPoolService is not None
