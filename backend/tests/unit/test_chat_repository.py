"""Unit tests for ChatRepository."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.infrastructure.database.models.chat import ChatRoom, ChatMember, ChatMessage
from app.infrastructure.repositories.chat_repository import ChatRepository


@pytest.fixture
def sample_room_data():
    """Sample room data for testing."""
    return {
        "room_type": "direct",
        "room_name": "Test Room",
        "room_metadata": {"type": "direct", "user_ids": ["user1", "user2"]},
    }


@pytest.fixture
def sample_member_data():
    """Sample member data for testing."""
    return {
        "user_id": "test_user",
        "role": "member",
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "sender_id": "test_user",
        "content": "Test message",
        "message_type": "text",
    }


class TestChatRepository:
    """Test suite for ChatRepository."""

    @pytest.mark.asyncio
    async def test_create_room(self, db_session, sample_room_data):
        """Test creating a chat room."""
        repository = ChatRepository(db_session)

        room = await repository.create_room(sample_room_data)

        assert room.room_id is not None
        assert room.room_type == "direct"
        assert room.room_name == "Test Room"
        assert room.is_active is True

    @pytest.mark.asyncio
    async def test_get_room_by_id(self, db_session, sample_room_data):
        """Test retrieving a room by ID."""
        repository = ChatRepository(db_session)

        created_room = await repository.create_room(sample_room_data)
        retrieved_room = await repository.get_room_by_id(created_room.room_id)

        assert retrieved_room is not None
        assert retrieved_room.room_id == created_room.room_id
        assert retrieved_room.room_name == created_room.room_name

    @pytest.mark.asyncio
    async def test_get_user_rooms(self, db_session, sample_room_data, sample_member_data):
        """Test getting all rooms for a user."""
        repository = ChatRepository(db_session)

        # Create room
        room = await repository.create_room(sample_room_data)

        # Add member
        member_data = {**sample_member_data, "room_id": room.room_id}
        await repository.add_member(member_data)

        # Get user rooms
        rooms = await repository.get_user_rooms("test_user")

        assert len(rooms) == 1
        assert rooms[0].room_id == room.room_id

    @pytest.mark.asyncio
    async def test_get_direct_room(self, db_session):
        """Test finding existing direct room between two users."""
        repository = ChatRepository(db_session)

        # Create direct room
        room_data = {
            "room_type": "direct",
            "room_metadata": {"type": "direct", "user_ids": ["user1", "user2"]},
        }
        created_room = await repository.create_room(room_data)

        # Find room
        found_room = await repository.get_direct_room("user1", "user2")

        assert found_room is not None
        assert found_room.room_id == created_room.room_id

    @pytest.mark.asyncio
    async def test_add_member(self, db_session, sample_room_data, sample_member_data):
        """Test adding a member to a room."""
        repository = ChatRepository(db_session)

        room = await repository.create_room(sample_room_data)
        member_data = {**sample_member_data, "room_id": room.room_id}

        member = await repository.add_member(member_data)

        assert member.member_id is not None
        assert member.user_id == "test_user"
        assert member.room_id == room.room_id

    @pytest.mark.asyncio
    async def test_create_message(self, db_session, sample_room_data, sample_message_data):
        """Test creating a message."""
        repository = ChatRepository(db_session)

        room = await repository.create_room(sample_room_data)
        message_data = {**sample_message_data, "room_id": room.room_id}

        message = await repository.create_message(message_data)

        assert message.message_id is not None
        assert message.content == "Test message"
        assert message.sender_id == "test_user"
        assert message.is_deleted is False

    @pytest.mark.asyncio
    async def test_get_messages(self, db_session, sample_room_data, sample_message_data):
        """Test retrieving messages from a room."""
        repository = ChatRepository(db_session)

        room = await repository.create_room(sample_room_data)

        # Create multiple messages
        for i in range(3):
            message_data = {
                **sample_message_data,
                "room_id": room.room_id,
                "content": f"Message {i}",
            }
            await repository.create_message(message_data)

        # Get messages
        messages = await repository.get_messages(room.room_id, limit=10)

        assert len(messages) == 3
        assert messages[0].content == "Message 0"  # Chronological order

    @pytest.mark.asyncio
    async def test_update_message(self, db_session, sample_room_data, sample_message_data):
        """Test updating a message."""
        repository = ChatRepository(db_session)

        room = await repository.create_room(sample_room_data)
        message_data = {**sample_message_data, "room_id": room.room_id}
        message = await repository.create_message(message_data)

        # Update message
        updated = await repository.update_message(message.message_id, "Updated content")

        assert updated is not None
        assert updated.content == "Updated content"
        assert updated.is_edited is True

    @pytest.mark.asyncio
    async def test_delete_message(self, db_session, sample_room_data, sample_message_data):
        """Test soft deleting a message."""
        repository = ChatRepository(db_session)

        room = await repository.create_room(sample_room_data)
        message_data = {**sample_message_data, "room_id": room.room_id}
        message = await repository.create_message(message_data)

        # Delete message
        deleted = await repository.delete_message(message.message_id)

        assert deleted is not None
        assert deleted.is_deleted is True
        assert deleted.deleted_at is not None

    @pytest.mark.asyncio
    async def test_search_messages(self, db_session, sample_room_data, sample_message_data):
        """Test searching messages."""
        repository = ChatRepository(db_session)

        room = await repository.create_room(sample_room_data)

        # Create messages with different content
        messages_content = ["Hello world", "Test message", "Another test"]
        for content in messages_content:
            message_data = {
                **sample_message_data,
                "room_id": room.room_id,
                "content": content,
            }
            await repository.create_message(message_data)

        # Search for "test"
        results = await repository.search_messages(room.room_id, "test")

        assert len(results) == 2
        assert all("test" in msg.content.lower() for msg in results)

    @pytest.mark.asyncio
    async def test_mark_as_read(self, db_session, sample_room_data, sample_member_data):
        """Test updating member's read status."""
        repository = ChatRepository(db_session)

        room = await repository.create_room(sample_room_data)
        member_data = {**sample_member_data, "room_id": room.room_id}
        member = await repository.add_member(member_data)

        # Mark as read
        now = datetime.now(timezone.utc)
        updated = await repository.update_member_read_status(
            room.room_id, "test_user", now
        )

        assert updated is not None
        assert updated.last_read_at == now
        assert updated.unread_count == 0
