"""Unit tests for ChatService."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.domain.chat.schemas import DirectChatCreate, MessageCreate, TeamChatCreate
from app.domain.chat.service import ChatService
from app.infrastructure.database.models.chat import ChatRoom


@pytest.fixture
def mock_repository():
    """Mock ChatRepository."""
    repository = AsyncMock()
    repository.session = AsyncMock()
    repository.session.commit = AsyncMock()
    return repository


@pytest.fixture
def chat_service(mock_repository):
    """ChatService with mocked repository."""
    return ChatService(mock_repository)


class TestChatService:
    """Test suite for ChatService."""

    @pytest.mark.asyncio
    async def test_create_direct_chat_new(self, chat_service, mock_repository):
        """Test creating a new direct chat."""
        # Setup
        user_id = "user1"
        data = DirectChatCreate(recipient_id="user2")
        mock_repository.get_direct_room = AsyncMock(return_value=None)

        mock_room = ChatRoom(
            room_id=uuid4(),
            room_type="direct",
            room_name=None,
            description=None,
            display_mode="open",
            is_active=True,
            is_archived=False,
            room_metadata={"type": "direct", "user_ids": sorted([user_id, "user2"])}
        )
        mock_room.created_at = datetime.now(UTC)
        mock_room.updated_at = datetime.now(UTC)

        mock_repository.create_room = AsyncMock(return_value=mock_room)
        mock_repository.get_room_by_id = AsyncMock(return_value=mock_room)
        mock_repository.get_member = AsyncMock(return_value=Mock(is_active=True))
        mock_repository.get_room_unread_count = AsyncMock(return_value=0)
        mock_repository.get_room_members = AsyncMock(return_value=[])
        mock_repository.add_member = AsyncMock()

        # Execute
        result = await chat_service.create_direct_chat(user_id, data)

        # Assert
        assert mock_repository.create_room.called
        assert mock_repository.add_member.call_count == 2
        assert result.room_type == "direct"

    @pytest.mark.asyncio
    async def test_create_direct_chat_existing(self, chat_service, mock_repository):
        """Test getting existing direct chat."""
        # Setup
        user_id = "user1"
        data = DirectChatCreate(recipient_id="user2")
        existing_room = ChatRoom(
            room_id=uuid4(),
            room_type="direct",
            room_name=None,
            description=None,
            display_mode="open",
            is_active=True,
            is_archived=False,
            room_metadata={"type": "direct", "user_ids": sorted([user_id, "user2"])}
        )
        existing_room.created_at = datetime.now(UTC)
        existing_room.updated_at = datetime.now(UTC)

        mock_repository.get_direct_room = AsyncMock(return_value=existing_room)
        mock_repository.get_room_by_id = AsyncMock(return_value=existing_room)
        mock_repository.get_member = AsyncMock(return_value=Mock(is_active=True))
        mock_repository.get_room_unread_count = AsyncMock(return_value=0)
        mock_repository.get_room_members = AsyncMock(return_value=[])

        # Execute
        result = await chat_service.create_direct_chat(user_id, data)

        # Assert
        assert not mock_repository.create_room.called
        assert result.room_id == existing_room.room_id

    @pytest.mark.asyncio
    async def test_create_team_chat(self, chat_service, mock_repository):
        """Test creating a team chat."""
        # Setup
        user_id = "user1"
        data = TeamChatCreate(
            team_id=uuid4(),
            room_name="Team Channel",
            description="Test channel",
        )
        mock_room = ChatRoom(
            room_id=uuid4(),
            room_type="team",
            room_name="Team Channel",
            description="Test channel",
            display_mode="open",
            is_active=True,
            is_archived=False,
            room_metadata={"type": "team", "team_id": str(data.team_id)}
        )
        mock_room.created_at = datetime.now(UTC)
        mock_room.updated_at = datetime.now(UTC)

        mock_repository.create_room = AsyncMock(return_value=mock_room)
        mock_repository.add_member = AsyncMock()

        # Execute
        result = await chat_service.create_team_chat(user_id, data)

        # Assert
        assert mock_repository.create_room.called
        assert result.room_name == "Team Channel"

    @pytest.mark.asyncio
    async def test_get_rooms(self, chat_service, mock_repository):
        """Test getting user's rooms."""
        # Setup
        user_id = "user1"
        mock_room1 = ChatRoom(
            room_id=uuid4(),
            room_type="team",
            room_name="Room 1",
            description=None,
            display_mode="open",
            is_active=True,
            is_archived=False,
            room_metadata={}
        )
        mock_room1.created_at = datetime.now(UTC)
        mock_room1.updated_at = datetime.now(UTC)

        mock_room2 = ChatRoom(
            room_id=uuid4(),
            room_type="team",
            room_name="Room 2",
            description=None,
            display_mode="open",
            is_active=True,
            is_archived=False,
            room_metadata={}
        )
        mock_room2.created_at = datetime.now(UTC)
        mock_room2.updated_at = datetime.now(UTC)

        mock_repository.get_user_rooms = AsyncMock(return_value=[mock_room1, mock_room2])
        mock_repository.get_last_message = AsyncMock(return_value=None)
        mock_repository.get_room_unread_count = AsyncMock(return_value=0)

        # Execute
        result = await chat_service.get_user_rooms(user_id)

        # Assert
        assert len(result) == 2
        assert result[0].room_name == "Room 1"

    @pytest.mark.asyncio
    async def test_send_message(self, chat_service, mock_repository):
        """Test sending a message."""
        # Setup
        room_id = uuid4()
        user_id = "user1"
        data = MessageCreate(content="Hello", message_type="text")

        mock_repository.get_member = AsyncMock(return_value=Mock(is_active=True))

        from app.infrastructure.database.models.chat import ChatMessage
        mock_message = ChatMessage(
            message_id=uuid4(),
            room_id=room_id,
            sender_id=user_id,
            message_type="text",
            content="Hello",
            attachments=[],
            parent_message_id=None,
            thread_count=0,
            reactions=[],
            is_edited=False,
            is_deleted=False,
        )
        mock_message.created_at = datetime.now(UTC)
        mock_message.updated_at = datetime.now(UTC)

        mock_repository.create_message = AsyncMock(return_value=mock_message)

        # Execute
        result = await chat_service.send_message(room_id, user_id, data)

        # Assert
        assert result.content == "Hello"

    @pytest.mark.asyncio
    async def test_update_message(self, chat_service, mock_repository):
        """Test updating a message."""
        # Setup
        message_id = uuid4()
        user_id = "user1"
        new_content = "Updated content"

        from app.infrastructure.database.models.chat import ChatMessage
        mock_message = ChatMessage(
            message_id=message_id,
            room_id=uuid4(),
            sender_id=user_id,
            message_type="text",
            content="old content",
            attachments=[],
            parent_message_id=None,
            thread_count=0,
            reactions=[],
            is_edited=False,
            is_deleted=False,
        )
        mock_message.created_at = datetime.now(UTC)
        mock_message.updated_at = datetime.now(UTC)

        mock_repository.get_message_by_id = AsyncMock(return_value=mock_message)

        # Room update return
        updated_mock = ChatMessage(
            message_id=message_id,
            room_id=mock_message.room_id,
            sender_id=user_id,
            message_type="text",
            content=new_content,
            attachments=[],
            parent_message_id=None,
            thread_count=0,
            reactions=[],
            is_edited=True,
            is_deleted=False,
        )
        updated_mock.created_at = mock_message.created_at
        updated_mock.updated_at = datetime.now(UTC)

        mock_repository.update_message = AsyncMock(return_value=updated_mock)

        # Execute
        result = await chat_service.update_message(message_id, user_id, new_content)

        # Assert
        assert result.content == new_content

    @pytest.mark.asyncio
    async def test_delete_message(self, chat_service, mock_repository):
        """Test deleting a message."""
        # Setup
        message_id = uuid4()
        user_id = "user1"

        from app.infrastructure.database.models.chat import ChatMessage
        mock_message = ChatMessage(
            message_id=message_id,
            room_id=uuid4(),
            sender_id=user_id,
            message_type="text",
            content="To delete",
            attachments=[],
            parent_message_id=None,
            thread_count=0,
            reactions=[],
            is_edited=False,
            is_deleted=False,
        )
        mock_repository.get_message_by_id = AsyncMock(return_value=mock_message)

        deleted_mock = ChatMessage(
            message_id=message_id,
            room_id=mock_message.room_id,
            sender_id=user_id,
            message_type="text",
            content="To delete",
            attachments=[],
            parent_message_id=None,
            thread_count=0,
            reactions=[],
            is_edited=False,
            is_deleted=True,
        )
        deleted_mock.created_at = datetime.now(UTC)
        deleted_mock.updated_at = datetime.now(UTC)

        mock_repository.delete_message = AsyncMock(return_value=deleted_mock)

        # Execute
        result = await chat_service.delete_message(message_id, user_id)

        # Assert
        assert result.is_deleted is True
