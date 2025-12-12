"""Integration tests for Chat API endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.main import app


@pytest.fixture
async def client():
    """Create async HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers."""
    # In real tests, generate actual JWT token
    return {"Authorization": f"Bearer test_token_{test_user['id']}"}


class TestChatRoomEndpoints:
    """Test suite for chat room endpoints."""

    @pytest.mark.asyncio
    async def test_get_user_rooms(self, client, auth_headers):
        """Test getting user's chat rooms."""
        response = await client.get("/api/v1/chats/rooms", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_create_direct_chat(self, client, auth_headers):
        """Test creating a direct chat."""
        payload = {"recipient_id": "user2"}

        response = await client.post(
            "/api/v1/chats/rooms/direct",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["room_type"] == "direct"
        assert "room_id" in data

    @pytest.mark.asyncio
    async def test_create_team_chat(self, client, auth_headers):
        """Test creating a team chat."""
        payload = {
            "team_id": str(uuid4()),
            "room_name": "Test Team Channel",
            "description": "Test description",
        }

        response = await client.post(
            "/api/v1/chats/rooms/team",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["room_type"] == "team"
        assert data["room_name"] == "Test Team Channel"

    @pytest.mark.asyncio
    async def test_get_room_details(self, client, auth_headers):
        """Test getting room details."""
        # First create a room
        create_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = create_response.json()["room_id"]

        # Get room details
        response = await client.get(
            f"/api/v1/chats/rooms/{room_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == room_id


class TestChatMessageEndpoints:
    """Test suite for chat message endpoints."""

    @pytest.mark.asyncio
    async def test_send_message(self, client, auth_headers):
        """Test sending a message."""
        # Create room first
        room_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = room_response.json()["room_id"]

        # Send message
        payload = {"content": "Hello, world!", "message_type": "text"}
        response = await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello, world!"
        assert "message_id" in data

    @pytest.mark.asyncio
    async def test_get_messages(self, client, auth_headers):
        """Test getting messages from a room."""
        # Create room and send message
        room_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = room_response.json()["room_id"]

        await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages",
            json={"content": "Test message", "message_type": "text"},
            headers=auth_headers,
        )

        # Get messages
        response = await client.get(
            f"/api/v1/chats/rooms/{room_id}/messages",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) > 0

    @pytest.mark.asyncio
    async def test_update_message(self, client, auth_headers):
        """Test updating a message."""
        # Create room and message
        room_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = room_response.json()["room_id"]

        message_response = await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages",
            json={"content": "Original", "message_type": "text"},
            headers=auth_headers,
        )
        message_id = message_response.json()["message_id"]

        # Update message
        response = await client.patch(
            f"/api/v1/chats/rooms/{room_id}/messages/{message_id}",
            json={"content": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated"
        assert data["is_edited"] is True

    @pytest.mark.asyncio
    async def test_delete_message(self, client, auth_headers):
        """Test deleting a message."""
        # Create room and message
        room_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = room_response.json()["room_id"]

        message_response = await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages",
            json={"content": "To be deleted", "message_type": "text"},
            headers=auth_headers,
        )
        message_id = message_response.json()["message_id"]

        # Delete message
        response = await client.delete(
            f"/api/v1/chats/rooms/{room_id}/messages/{message_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_deleted"] is True

    @pytest.mark.asyncio
    async def test_search_messages(self, client, auth_headers):
        """Test searching messages."""
        # Create room and messages
        room_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = room_response.json()["room_id"]

        # Send messages with searchable content
        await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages",
            json={"content": "Hello world", "message_type": "text"},
            headers=auth_headers,
        )
        await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages",
            json={"content": "Test message", "message_type": "text"},
            headers=auth_headers,
        )

        # Search
        response = await client.get(
            f"/api/v1/chats/rooms/{room_id}/search?q=hello",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) > 0
        assert "hello" in data["messages"][0]["content"].lower()

    @pytest.mark.asyncio
    async def test_mark_as_read(self, client, auth_headers):
        """Test marking messages as read."""
        # Create room
        room_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = room_response.json()["room_id"]

        # Mark as read
        response = await client.post(
            f"/api/v1/chats/rooms/{room_id}/read",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Marked as read"


class TestChatReactionEndpoints:
    """Test suite for message reaction endpoints."""

    @pytest.mark.asyncio
    async def test_add_reaction(self, client, auth_headers):
        """Test adding a reaction to a message."""
        # Create room and message
        room_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = room_response.json()["room_id"]

        message_response = await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages",
            json={"content": "React to this", "message_type": "text"},
            headers=auth_headers,
        )
        message_id = message_response.json()["message_id"]

        # Add reaction
        response = await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages/{message_id}/react?emoji=👍",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reactions" in data

    @pytest.mark.asyncio
    async def test_remove_reaction(self, client, auth_headers):
        """Test removing a reaction from a message."""
        # Create room, message, and add reaction
        room_response = await client.post(
            "/api/v1/chats/rooms/direct",
            json={"recipient_id": "user2"},
            headers=auth_headers,
        )
        room_id = room_response.json()["room_id"]

        message_response = await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages",
            json={"content": "React to this", "message_type": "text"},
            headers=auth_headers,
        )
        message_id = message_response.json()["message_id"]

        await client.post(
            f"/api/v1/chats/rooms/{room_id}/messages/{message_id}/react?emoji=👍",
            headers=auth_headers,
        )

        # Remove reaction
        response = await client.delete(
            f"/api/v1/chats/rooms/{room_id}/messages/{message_id}/react?emoji=👍",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Reaction removed"
