"""Unit tests for ChatService."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from app.domain.chat.service import ChatService
from app.domain.chat.schemas import DirectChatCreate, MessageCreate, TeamChatCreate


@pytest.fixture
def mock_repository():
    """Mock ChatRepository."""
    repository = Mock()
    repository.session = Mock()
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
        mock_repository.create_room = AsyncMock(return_value=Mock(room_id=uuid4()))
        mock_repository.add_member = AsyncMock()

        # Execute
        result = await chat_service.create_direct_chat(user_id, data)

        # Assert
        assert mock_repository.create_room.called
        assert mock_repository.add_member.call_count == 2  # Two members

    @pytest.mark.asyncio
    async def test_create_direct_chat_existing(self, chat_service, mock_repository):
        """Test getting existing direct chat."""
        # Setup
        user_id = "user1"
        data = DirectChatCreate(recipient_id="user2")
        existing_room = Mock(room_id=uuid4())
        mock_repository.get_direct_room = AsyncMock(return_value=existing_room)

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
        mock_repository.create_room = AsyncMock(return_value=Mock(room_id=uuid4()))
        mock_repository.add_member = AsyncMock()

        # Execute
        result = await chat_service.create_team_chat(user_id, data)

        # Assert
        assert mock_repository.create_room.called
        assert mock_repository.add_member.called

    @pytest.mark.asyncio
    async def test_send_message(self, chat_service, mock_repository):
        """Test sending a message."""
        # Setup
        room_id = uuid4()
        user_id = "user1"
        data = MessageCreate(content="Hello", message_type="text")

        mock_member = Mock()
        mock_repository.get_member = AsyncMock(return_value=mock_member)
        mock_repository.create_message = AsyncMock(
            return_value=Mock(
                message_id=uuid4(),
                content="Hello",
                sender_id=user_id,
            )
        )

        # Execute
        result = await chat_service.send_message(room_id, user_id, data)

        # Assert
        assert mock_repository.create_message.called
        assert result.content == "Hello"

    @pytest.mark.asyncio
    async def test_send_message_not_member(self, chat_service, mock_repository):
        """Test sending message when not a member."""
        # Setup
        room_id = uuid4()
        user_id = "user1"
        data = MessageCreate(content="Hello", message_type="text")

        mock_repository.get_member = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(ValueError, match="Not a member"):
            await chat_service.send_message(room_id, user_id, data)

    @pytest.mark.asyncio
    async def test_update_message(self, chat_service, mock_repository):
        """Test updating a message."""
        # Setup
        message_id = uuid4()
        user_id = "user1"
        new_content = "Updated content"

        mock_message = Mock(sender_id=user_id)
        mock_repository.get_message_by_id = AsyncMock(return_value=mock_message)
        mock_repository.update_message = AsyncMock(
            return_value=Mock(content=new_content)
        )

        # Execute
        result = await chat_service.update_message(message_id, user_id, new_content)

        # Assert
        assert mock_repository.update_message.called
        assert result.content == new_content

    @pytest.mark.asyncio
    async def test_update_message_not_sender(self, chat_service, mock_repository):
        """Test updating message when not the sender."""
        # Setup
        message_id = uuid4()
        user_id = "user1"
        new_content = "Updated content"

        mock_message = Mock(sender_id="other_user")
        mock_repository.get_message_by_id = AsyncMock(return_value=mock_message)

        # Execute & Assert
        with pytest.raises(ValueError, match="Not the sender"):
            await chat_service.update_message(message_id, user_id, new_content)

    @pytest.mark.asyncio
    async def test_delete_message(self, chat_service, mock_repository):
        """Test deleting a message."""
        # Setup
        message_id = uuid4()
        user_id = "user1"

        mock_message = Mock(sender_id=user_id)
        mock_repository.get_message_by_id = AsyncMock(return_value=mock_message)
        mock_repository.delete_message = AsyncMock(return_value=mock_message)

        # Execute
        result = await chat_service.delete_message(message_id, user_id)

        # Assert
        assert mock_repository.delete_message.called

    @pytest.mark.asyncio
    async def test_mark_as_read(self, chat_service, mock_repository):
        """Test marking messages as read."""
        # Setup
        room_id = uuid4()
        user_id = "user1"

        mock_repository.update_member_read_status = AsyncMock()

        # Execute
        await chat_service.mark_as_read(room_id, user_id)

        # Assert
        assert mock_repository.update_member_read_status.called

    @pytest.mark.asyncio
    async def test_get_rooms(self, chat_service, mock_repository):
        """Test getting user's rooms."""
        # Setup
        user_id = "user1"
        mock_rooms = [
            Mock(room_id=uuid4(), room_name="Room 1"),
            Mock(room_id=uuid4(), room_name="Room 2"),
        ]
        mock_repository.get_user_rooms = AsyncMock(return_value=mock_rooms)
        mock_repository.get_unread_count = AsyncMock(return_value=5)

        # Execute
        result = await chat_service.get_user_rooms(user_id)

        # Assert
        assert len(result.rooms) == 2
        assert result.total == 2
