"""Unit tests for community service."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock

from app.domain.community.service import CommunityService
from app.domain.community.schemas import PostCreate
from app.infrastructure.repositories.community_repository import CommunityRepository


@pytest.fixture
def mock_community_repository():
    """Create mock community repository."""
    return AsyncMock(spec=CommunityRepository)


@pytest.fixture
def community_service(mock_community_repository):
    """Create community service with mocked dependencies."""
    return CommunityService(repository=mock_community_repository)


class TestCommunityService:
    """Test cases for CommunityService."""

    @pytest.mark.asyncio
    async def test_create_post(self, community_service, mock_community_repository):
        """Test creating a community post."""
        user_id = str(uuid4())
        post_data = PostCreate(
            title="Test Post",
            content="This is a test post content",
            category="general",
        )

        expected_post = {
            "id": str(uuid4()),
            "title": "Test Post",
            "content": "This is a test post content",
            "author_id": user_id,
            "category": "general",
            "created_at": datetime.utcnow(),
        }

        mock_community_repository.create_post.return_value = expected_post

        result = await community_service.create_post(user_id, post_data)

        assert result is not None
        assert result["title"] == "Test Post"
        assert result["author_id"] == user_id
        mock_community_repository.create_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_posts_by_category(self, community_service, mock_community_repository):
        """Test getting posts by category."""
        category = "study"
        expected_posts = [
            {"id": str(uuid4()), "title": "Study Tips", "category": "study"},
            {"id": str(uuid4()), "title": "Focus Techniques", "category": "study"},
        ]

        mock_community_repository.get_by_category.return_value = expected_posts

        result = await community_service.get_posts_by_category(category)

        assert len(result) == 2
        assert all(post["category"] == "study" for post in result)


def test_community_service_import():
    """Test that community service can be imported."""
    from app.domain.community.service import CommunityService
    assert CommunityService is not None
