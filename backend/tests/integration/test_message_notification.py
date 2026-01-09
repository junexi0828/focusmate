
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.messaging.service import MessagingService
from app.domain.notification.service import NotificationService
from datetime import datetime
from app.domain.messaging.schemas import MessageCreate
from app.domain.notification.schemas import NotificationPriority

@pytest.mark.asyncio
async def test_send_message_triggers_notification():
    # Mocks
    conversation_repo = AsyncMock()
    message_repo = AsyncMock()
    user_repo = AsyncMock()
    notification_service = AsyncMock(spec=NotificationService)

    # Setup Service
    service = MessagingService(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
        user_repo=user_repo,
        notification_service=notification_service
    )

    # Mock Data
    sender_id = "sender_123"
    receiver_id = "receiver_456"
    message_data = MessageCreate(receiver_id=receiver_id, content="Hello World")

    # Mock Repository Responses
    user_repo.get_by_id.side_effect = lambda uid: MagicMock(username="TestUser") if uid in [sender_id, receiver_id] else None
    conversation_repo.get_by_participants.return_value = None # New conversation

    new_conv = MagicMock(id="conv_123", user1_id=sender_id, user2_id=receiver_id)
    conversation_repo.create.return_value = new_conv

    created_message = MagicMock(
        id="msg_123",
        conversation_id="conv_123",
        created_at=datetime(2023, 1, 1, 0, 0, 0),
        sender_id=sender_id,
        receiver_id=receiver_id,
        content="Hello World",
        is_read=False,
        read_at=None,
        sender_username=None,
        receiver_username=None
    )
    message_repo.create.return_value = created_message

    # Execute
    await service.send_message(sender_id, message_data)

    # Verify Notification
    assert notification_service.create_notification.called
    call_args = notification_service.create_notification.call_args[0][0]

    assert call_args.user_id == receiver_id
    assert call_args.type == "new_message"
    assert call_args.priority == NotificationPriority.HIGH
    assert call_args.group_key == "message:conv_123"
    assert call_args.routing["path"] == "/messages/conversations/conv_123"
