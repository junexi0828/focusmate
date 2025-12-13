"""Unit tests for room service."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from app.domain.room.service import RoomService
from app.domain.room.schemas import RoomCreate
from app.infrastructure.repositories.room_repository import RoomRepository


@pytest.fixture
def mock_room_repository():
    """Create mock room repository."""
    return AsyncMock(spec=RoomRepository)


@pytest.fixture
def room_service(mock_room_repository):
    """Create room service with mocked dependencies."""
    return RoomService(repository=mock_room_repository)


class TestRoomService:
    """Test cases for RoomService."""

    @pytest.mark.asyncio
    async def test_create_room(self, room_service, mock_room_repository):
        """Test creating a room."""
        user_id = str(uuid4())
        room_data = RoomCreate(
            name="Study Session",
            work_duration=1500,
            break_duration=300,
        )

        expected_room = {
            "id": str(uuid4()),
            "name": "Study Session",
            "host_id": user_id,
            "work_duration": 1500,
            "break_duration": 300,
            "status": "waiting",
        }

        mock_room_repository.create.return_value = expected_room

        result = await room_service.create_room(user_id, room_data)

        assert result is not None
        assert result["name"] == "Study Session"
        assert result["host_id"] == user_id
        mock_room_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_rooms(self, room_service, mock_room_repository):
        """Test getting active rooms."""
        expected_rooms = [
            {"id": str(uuid4()), "name": "Room 1", "status": "active"},
            {"id": str(uuid4()), "name": "Room 2", "status": "active"},
        ]

        mock_room_repository.get_active.return_value = expected_rooms

        result = await room_service.get_active_rooms()

        assert len(result) == 2
        assert all(room["status"] == "active" for room in result)


def test_room_service_import():
    """Test that room service can be imported."""
    from app.domain.room.service import RoomService
    assert RoomService is not None
