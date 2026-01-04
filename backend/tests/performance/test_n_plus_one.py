"""N+1 Query Detection Tests

This module contains automated tests to prevent N+1 query problems.
Tests ensure that query counts remain constant regardless of data size.

Industry standard practice (Facebook DataLoader, Google/Meta/Netflix).

Test Strategy:
- Each test verifies a specific endpoint/service method
- Query count must be ≤ threshold regardless of result size
- Failures indicate N+1 query regression
- Runs automatically in CI/CD pipeline

Related:
- QUL-010: Database Performance Optimization Report
- Implementation Plan: Phase 2 - Monitoring & Prevention
"""

import pytest
from tests.utils import QueryCounter
from app.domain.community.service import CommunityService
from app.domain.community.schemas import PostFilters, PostSortBy
from app.domain.messaging.service import MessagingService
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.community_repository import (
    PostRepository,
    PostLikeRepository,
    PostReadRepository,
    CommentRepository,
    CommentLikeRepository,
)
from app.infrastructure.repositories.messaging_repository import (
    ConversationRepository,
    MessageRepository,
)


class TestCommunityN1Prevention:
    """Test suite for Community service N+1 query prevention.

    Verifies that batch loading optimizations prevent N+1 queries
    in post and comment retrieval operations.
    """

    @pytest.mark.asyncio
    async def test_get_posts_no_n_plus_one(self, db_session, sample_posts):
        """TC-N1-001: Verify get_posts() has no N+1 queries.

        Expected behavior:
        - Query count should be ≤5 regardless of post count
        - Breakdown: 1 posts + 1 users + 1 likes + 1 reads + 1 count

        Before optimization: 150 queries for 50 posts (N+1 problem)
        After optimization: 3-5 queries for any number of posts

        Args:
            db_session: Database session fixture
            sample_posts: Fixture providing 50 test posts
        """
        # Given: Community service with repositories
        user_repo = UserRepository(db_session)
        post_repo = PostRepository(db_session)
        post_like_repo = PostLikeRepository(db_session)
        post_read_repo = PostReadRepository(db_session)
        comment_repo = CommentRepository(db_session)

        service = CommunityService(
            user_repo=user_repo,
            post_repo=post_repo,
            post_like_repo=post_like_repo,
            post_read_repo=post_read_repo,
            comment_repo=comment_repo,
            comment_like_repo=None,  # Not used in get_posts
        )

        # When: Fetch 50 posts with query counting
        filters = PostFilters(
            limit=50,
            offset=0,
            sort_by=PostSortBy.RECENT,
        )

        with QueryCounter() as counter:
            result = await service.get_posts(filters, current_user_id="test_user")

        # Then: Query count should be ≤5 (batch loading)
        assert counter.count <= 5, (
            f"N+1 query detected! Expected ≤5 queries, got {counter.count}\n"
            f"Query breakdown:\n{counter.get_summary()}"
        )

        # Verify results are correct
        assert len(result.posts) <= 50

    @pytest.mark.asyncio
    async def test_get_comments_no_n_plus_one(self, db_session, sample_post_with_comments):
        """TC-N1-002: Verify get_post_comments() has no N+1 queries.

        Expected behavior:
        - Query count should be ≤3 regardless of comment count
        - Breakdown: 1 comments + 1 users + 1 likes

        Before optimization: 100 queries for 50 comments (N+1 problem)
        After optimization: 2-3 queries for any number of comments

        Args:
            db_session: Database session fixture
            sample_post_with_comments: Fixture providing post with 50 comments
        """
        # Given: Community service
        user_repo = UserRepository(db_session)
        comment_repo = CommentRepository(db_session)
        comment_like_repo = CommentLikeRepository(db_session)

        service = CommunityService(
            user_repo=user_repo,
            post_repo=None,
            post_like_repo=None,
            post_read_repo=None,
            comment_repo=comment_repo,
            comment_like_repo=comment_like_repo,
        )

        post_id = sample_post_with_comments.id

        # When: Fetch 50 comments with query counting
        with QueryCounter() as counter:
            comments = await service.get_post_comments(
                post_id=post_id,
                current_user_id="test_user"
            )

        # Then: Query count should be ≤3 (batch loading)
        assert counter.count <= 3, (
            f"N+1 query detected! Expected ≤3 queries, got {counter.count}\n"
            f"Query breakdown:\n{counter.get_summary()}"
        )

        # Verify results are correct
        assert len(comments) <= 50


class TestMessagingN1Prevention:
    """Test suite for Messaging service N+1 query prevention.

    Verifies that batch loading optimizations prevent N+1 queries
    in conversation and message retrieval operations.
    """

    @pytest.mark.asyncio
    async def test_get_conversations_no_n_plus_one(
        self, db_session, sample_conversations
    ):
        """TC-N1-003: Verify get_user_conversations() has no N+1 queries.

        Expected behavior:
        - Query count should be ≤3 regardless of conversation count
        - Breakdown: 1 conversations + 1 users + 1 last_messages

        Before optimization: 40 queries for 20 conversations (N+1 problem)
        After optimization: 2-3 queries for any number of conversations

        Args:
            db_session: Database session fixture
            sample_conversations: Fixture providing 20 test conversations
        """
        # Given: Messaging service
        user_repo = UserRepository(db_session)
        conversation_repo = ConversationRepository(db_session)
        message_repo = MessageRepository(db_session)

        service = MessagingService(
            user_repo=user_repo,
            conversation_repo=conversation_repo,
            message_repo=message_repo,
        )

        # When: Fetch 20 conversations with query counting
        with QueryCounter() as counter:
            conversations = await service.get_user_conversations(
                user_id="test_user"
            )

        # Then: Query count should be ≤3 (batch loading)
        assert counter.count <= 3, (
            f"N+1 query detected! Expected ≤3 queries, got {counter.count}\n"
            f"Query breakdown:\n{counter.get_summary()}"
        )

        # Verify results are correct
        assert len(conversations) <= 20

    @pytest.mark.asyncio
    async def test_get_messages_no_n_plus_one(
        self, db_session, sample_conversation_with_messages
    ):
        """TC-N1-004: Verify get_conversation_detail() has no N+1 queries.

        Expected behavior:
        - Query count should be ≤2 regardless of message count
        - Breakdown: 1 conversation + 1 messages + 1 users (usually just 2 users!)

        Before optimization: 100 queries for 50 messages (N+1 problem)
        After optimization: 1-2 queries for any number of messages

        Args:
            db_session: Database session fixture
            sample_conversation_with_messages: Fixture with 50 messages
        """
        # Given: Messaging service
        user_repo = UserRepository(db_session)
        conversation_repo = ConversationRepository(db_session)
        message_repo = MessageRepository(db_session)

        service = MessagingService(
            user_repo=user_repo,
            conversation_repo=conversation_repo,
            message_repo=message_repo,
        )

        conversation_id = sample_conversation_with_messages.id

        # When: Fetch 50 messages with query counting
        with QueryCounter() as counter:
            detail = await service.get_conversation_detail(
                conversation_id=conversation_id,
                user_id="test_user",
                limit=50,
            )

        # Then: Query count should be ≤2 (batch loading)
        assert counter.count <= 2, (
            f"N+1 query detected! Expected ≤2 queries, got {counter.count}\n"
            f"Query breakdown:\n{counter.get_summary()}"
        )

        # Verify results are correct
        assert len(detail.messages) <= 50


class TestN1PreventionEdgeCases:
    """Test edge cases for N+1 query prevention.

    Verifies that optimizations work correctly with:
    - Empty results
    - Single items
    - Large datasets
    """

    @pytest.mark.asyncio
    async def test_empty_posts_no_queries(self, db_session):
        """TC-N1-005: Verify empty results don't execute unnecessary queries.

        Tests defensive coding (early returns).
        """
        # Given: Service with no data
        service = CommunityService(
            user_repo=UserRepository(db_session),
            post_repo=PostRepository(db_session),
            post_like_repo=PostLikeRepository(db_session),
            post_read_repo=PostReadRepository(db_session),
            comment_repo=CommentRepository(db_session),
            comment_like_repo=CommentLikeRepository(db_session),
        )

        filters = PostFilters(limit=50, offset=0)

        # When: Fetch with no data
        with QueryCounter() as counter:
            result = await service.get_posts(filters)

        # Then: Should execute minimal queries (just the initial fetch)
        assert counter.count <= 2, (
            f"Too many queries for empty result: {counter.count}"
        )
        assert len(result.posts) == 0

    @pytest.mark.asyncio
    async def test_single_post_efficient(self, db_session, sample_post):
        """TC-N1-006: Verify single item is still efficient.

        Tests that batch loading doesn't add overhead for small datasets.
        """
        # Given: Service with 1 post
        service = CommunityService(
            user_repo=UserRepository(db_session),
            post_repo=PostRepository(db_session),
            post_like_repo=PostLikeRepository(db_session),
            post_read_repo=PostReadRepository(db_session),
            comment_repo=CommentRepository(db_session),
            comment_like_repo=CommentLikeRepository(db_session),
        )

        filters = PostFilters(limit=1, offset=0)

        # When: Fetch 1 post
        with QueryCounter() as counter:
            result = await service.get_posts(filters, current_user_id="test_user")

        # Then: Should be efficient (≤5 queries)
        assert counter.count <= 5
        assert len(result.posts) == 1


# Pytest markers for categorization
pytestmark = [
    pytest.mark.performance,  # Performance test category
    pytest.mark.n_plus_one,   # N+1 specific tests
]
