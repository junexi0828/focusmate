"""Unit tests for community service."""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.community.schemas import PostCreate
from app.domain.community.service import CommunityService
from app.infrastructure.repositories.community_repository import (
    CommentLikeRepository,
    CommentRepository,
    PostLikeRepository,
    PostReadRepository,
    PostRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository


@pytest.fixture
def mock_post_repository():
    """Create mock post repository."""
    return AsyncMock(spec=PostRepository)


@pytest.fixture
def mock_comment_repository():
    """Create mock comment repository."""
    return AsyncMock(spec=CommentRepository)


@pytest.fixture
def mock_post_like_repository():
    """Create mock post like repository."""
    return AsyncMock(spec=PostLikeRepository)


@pytest.fixture
def mock_comment_like_repository():
    """Create mock comment like repository."""
    return AsyncMock(spec=CommentLikeRepository)


@pytest.fixture
def mock_post_read_repository():
    """Create mock post read repository."""
    return AsyncMock(spec=PostReadRepository)


@pytest.fixture
def mock_user_repository():
    """Create mock user repository."""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def community_service(
    mock_post_repository,
    mock_comment_repository,
    mock_post_like_repository,
    mock_comment_like_repository,
    mock_post_read_repository,
    mock_user_repository,
):
    """Create community service with mocked dependencies."""
    return CommunityService(
        post_repo=mock_post_repository,
        comment_repo=mock_comment_repository,
        post_like_repo=mock_post_like_repository,
        comment_like_repo=mock_comment_like_repository,
        post_read_repo=mock_post_read_repository,
        user_repo=mock_user_repository,
    )


class TestCommunityService:
    """Test cases for CommunityService."""

    @pytest.mark.asyncio
    async def test_create_post(self, community_service, mock_post_repository, mock_user_repository):
        """Test creating a community post."""
        from app.infrastructure.database.models.community import Post
        from app.infrastructure.database.models.user import User

        user_id = str(uuid4())
        post_data = PostCreate(
            title="Test Post",
            content="This is a test post content",
            category="general",
        )

        created_post = Post(
            id=str(uuid4()),
            user_id=user_id,
            title="Test Post",
            content="This is a test post content",
            category="general",
            likes=0,
            comment_count=0,
            is_pinned=False,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
        )

        mock_post_repository.create.return_value = created_post
        mock_user_repository.get_by_id.return_value = mock_user

        result = await community_service.create_post(user_id, post_data)

        assert result is not None
        assert result.title == "Test Post"
        assert result.user_id == user_id
        assert result.author_username == "testuser"
        mock_post_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_posts(self, community_service, mock_post_repository, mock_user_repository):
        """Test getting posts with filters."""
        from app.domain.community.schemas import PostFilters
        from app.infrastructure.database.models.community import Post
        from app.infrastructure.database.models.user import User

        post_id1 = str(uuid4())
        post_id2 = str(uuid4())
        user_id = str(uuid4())

        posts = [
            Post(
                id=post_id1,
                user_id=user_id,
                title="Study Tips",
                content="Content 1",
                category="study",
                likes=0,
                comment_count=0,
                is_pinned=False,
                is_deleted=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Post(
                id=post_id2,
                user_id=user_id,
                title="Focus Techniques",
                content="Content 2",
                category="study",
                likes=0,
                comment_count=0,
                is_pinned=False,
                is_deleted=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]

        mock_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
        )

        mock_post_repository.get_posts.return_value = (posts, 2)
        mock_user_repository.get_by_id.return_value = mock_user

        filters = PostFilters(category="study", limit=20, offset=0)
        result = await community_service.get_posts(filters)

        assert result.total == 2
        assert len(result.posts) == 2
        assert all(post.category == "study" for post in result.posts)


def test_community_service_import():
    """Test that community service can be imported."""
    from app.domain.community.service import CommunityService
    assert CommunityService is not None
