
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.domain.community.service import CommunityService
from app.domain.notification.service import NotificationService
from app.domain.community.schemas import CommentCreate
from app.domain.notification.schemas import NotificationPriority

@pytest.mark.asyncio
async def test_create_comment_triggers_notification():
    # Setup
    post_repo = AsyncMock()
    comment_repo = AsyncMock()
    post_like_repo = AsyncMock()
    comment_like_repo = AsyncMock()
    post_read_repo = AsyncMock()
    user_repo = AsyncMock()
    notification_service = AsyncMock(spec=NotificationService)

    service = CommunityService(
        post_repo=post_repo,
        comment_repo=comment_repo,
        post_like_repo=post_like_repo,
        comment_like_repo=comment_like_repo,
        post_read_repo=post_read_repo,
        user_repo=user_repo,
        notification_service=notification_service
    )

    # Mock Data
    post_author_id = "author_123"
    commenter_id = "commenter_456"
    post_id = "post_789"

    # Mock Post
    post = MagicMock(id=post_id, user_id=post_author_id, title="Test Post")
    post_repo.get_by_id.return_value = post

    # Mock User
    user_repo.get_by_id.return_value = MagicMock(username="CommenterUser")

    # Mock Comment Creation
    created_comment = MagicMock(
        id="comment_000",
        post_id=post_id,
        user_id=commenter_id,
        content="Nice post!",
        created_at=datetime(2023, 1, 1, 0, 0, 0),
        updated_at=datetime(2023, 1, 1, 0, 0, 0),
        parent_comment_id=None,
        likes=0,
        is_deleted=False,
        is_liked=False,
        replies=[],
        author_username=None
    )
    comment_repo.create.return_value = created_comment

    # Execute
    await service.create_comment(
        post_id,
        commenter_id,
        CommentCreate(content="Nice post!")
    )

    # Verify
    assert notification_service.create_notification.called
    call_args = notification_service.create_notification.call_args[0][0]

    assert call_args.user_id == post_author_id
    assert call_args.type == "post_comment"
    assert call_args.group_key == f"post_comment:{post_id}"
    assert call_args.routing["path"] == f"/community/posts/{post_id}"


@pytest.mark.asyncio
async def test_like_post_triggers_notification():
    # Setup (Reuse similar setup)
    post_repo = AsyncMock()
    comment_repo = AsyncMock()
    post_like_repo = AsyncMock()
    comment_like_repo = AsyncMock()
    post_read_repo = AsyncMock()
    user_repo = AsyncMock()
    notification_service = AsyncMock(spec=NotificationService)

    service = CommunityService(
        post_repo=post_repo,
        comment_repo=comment_repo,
        post_like_repo=post_like_repo,
        comment_like_repo=comment_like_repo,
        post_read_repo=post_read_repo,
        user_repo=user_repo,
        notification_service=notification_service
    )

    post_author_id = "author_123"
    liker_id = "liker_456"
    post_id = "post_789"

    post = MagicMock(id=post_id, user_id=post_author_id, title="Test Post", likes=0)
    post_repo.get_by_id.return_value = post
    post_like_repo.get_by_post_and_user.return_value = None # Not liked yet
    user_repo.get_by_id.return_value = MagicMock(username="LikerUser")

    # Execute
    await service.toggle_post_like(post_id, liker_id)

    # Verify
    assert notification_service.create_notification.called
    call_args = notification_service.create_notification.call_args[0][0]

    assert call_args.user_id == post_author_id
    assert call_args.type == "post_like"
    assert call_args.group_key == f"post_like:{post_id}"


@pytest.mark.asyncio
async def test_like_comment_triggers_notification():
    # Setup
    post_repo = AsyncMock()
    comment_repo = AsyncMock()
    post_like_repo = AsyncMock()
    comment_like_repo = AsyncMock()
    post_read_repo = AsyncMock()
    user_repo = AsyncMock()
    notification_service = AsyncMock(spec=NotificationService)

    service = CommunityService(
        post_repo=post_repo,
        comment_repo=comment_repo,
        post_like_repo=post_like_repo,
        comment_like_repo=comment_like_repo,
        post_read_repo=post_read_repo,
        user_repo=user_repo,
        notification_service=notification_service
    )

    comment_author_id = "comment_author_123"
    liker_id = "liker_456"
    post_id = "post_789"
    comment_id = "comment_000"

    # Mocks
    comment = MagicMock(
        id=comment_id,
        post_id=post_id,
        user_id=comment_author_id,
        content="My Comment",
        likes=0
    )
    comment_repo.get_by_id.return_value = comment
    comment_like_repo.get_by_comment_and_user.return_value = None

    post = MagicMock(id=post_id, title="Test Post")
    post_repo.get_by_id.return_value = post

    user_repo.get_by_id.return_value = MagicMock(username="LikerUser")

    # Execute
    try:
        # Debug: Check if Helper throws validation error locally
        from app.domain.notification.notification_helper import NotificationHelper
        NotificationHelper.create_comment_like_notification(
            user_id=comment_author_id,
            liker_name="LikerUser",
            post_id=post_id,
            post_title="Test Post",
            comment_content="My Comment"
        )
    except Exception as e:
        pytest.fail(f"Helper validation failed: {e}")

    await service.toggle_comment_like(comment_id, liker_id)

    # Verify logic flow
    assert comment_like_repo.create.called
    assert comment.likes == 1
    assert comment_repo.update.called

    # Verify Notification
    try:
        assert notification_service.create_notification.called
    except AssertionError:
        print(f"DEBUG: Mock calls: {notification_service.create_notification.mock_calls}")
        print(f"DEBUG: Parent calls: {notification_service.mock_calls}")
        raise

    call_args = notification_service.create_notification.call_args[0][0]

    assert call_args.user_id == comment_author_id
    assert call_args.type == "comment_like"
    assert call_args.group_key == f"post:{post_id}"
