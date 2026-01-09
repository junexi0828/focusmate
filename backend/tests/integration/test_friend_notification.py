
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from app.domain.friend.service import FriendService
from app.domain.notification.service import NotificationService
from app.domain.friend.schemas import FriendRequestCreate
from app.infrastructure.database.models.friend import FriendRequestStatus

@pytest.mark.asyncio
async def test_send_request_triggers_notification():
    # Setup
    friend_request_repo = AsyncMock()
    friend_repo = AsyncMock()
    notification_service = AsyncMock(spec=NotificationService)

    service = FriendService(
        friend_request_repo=friend_request_repo,
        friend_repo=friend_repo,
        notification_service=notification_service
    )

    sender_id = "sender_123"
    receiver_id = "receiver_456"

    # Mocks
    receiver = MagicMock(id=receiver_id, username="ReceiverUser", profile_image=None)
    friend_repo.get_user_by_id.side_effect = lambda uid: receiver if uid == receiver_id else MagicMock(id=sender_id, username="SenderUser", profile_image=None)

    # Existing checks
    friend_repo.get_friendship.return_value = None
    friend_request_repo.get_pending_request.return_value = None

    # Mock Request Creation
    new_request = MagicMock(
        id="req_000",
        sender_id=sender_id,
        receiver_id=receiver_id,
        status=FriendRequestStatus.PENDING,
        created_at=datetime.now(),
        responded_at=None
    )
    friend_request_repo.create_request.return_value = new_request

    # Execute
    await service.send_friend_request(
        sender_id,
        FriendRequestCreate(receiver_id=receiver_id)
    )

    # Verify
    assert notification_service.create_notification.called
    call_args = notification_service.create_notification.call_args[0][0]

    assert call_args.user_id == receiver_id
    assert call_args.type == "friend_request"
    assert call_args.group_key == f"friend_req:{new_request.id}"
    assert call_args.routing["path"] == "/friends/requests"

@pytest.mark.asyncio
async def test_accept_request_triggers_notification():
    # Setup
    friend_request_repo = AsyncMock()
    friend_repo = AsyncMock()
    notification_service = AsyncMock(spec=NotificationService)

    service = FriendService(
        friend_request_repo=friend_request_repo,
        friend_repo=friend_repo,
        notification_service=notification_service
    )

    request_id = "req_000"
    user_id = "receiver_456" # User accepting the request
    sender_id = "sender_123" # Original sender who gets verified

    # Mock Request
    request = MagicMock(
        id=request_id,
        sender_id=sender_id,
        receiver_id=user_id,
        status=FriendRequestStatus.PENDING
    )
    friend_request_repo.get_request_by_id.return_value = request
    friend_request_repo.update_request_status.return_value = request

    # Mock Users
    sender = MagicMock(id=sender_id, username="SenderUser", profile_image=None)
    receiver = MagicMock(id=user_id, username="ReceiverUser", profile_image=None)

    # get_user_by_id is called multiple times: for sender, for receiver
    # logic in service:
    # 1. get_request -> sender_id
    # 2. update status
    # 3. create friendship
    # 4. get sender info (get_user_by_id(sender_id))
    # 5. get receiver info (get_user_by_id(user_id)) -> needed for notification message

    async def get_user_mock(uid):
        if uid == sender_id: return sender
        if uid == user_id: return receiver
        return None

    friend_repo.get_user_by_id.side_effect = get_user_mock

    # Execute
    await service.accept_friend_request(request_id, user_id)

    # Verify
    assert notification_service.create_notification.called
    call_args = notification_service.create_notification.call_args[0][0]

    assert call_args.user_id == sender_id # Notification goes to initial sender
    assert call_args.type == "friend_request_accepted"
    assert call_args.group_key == f"friend:{user_id}"
    assert call_args.routing["path"] == "/friends"
