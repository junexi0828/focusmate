"""Unit tests for room service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.room.schemas import RoomCreate
from app.domain.room.service import RoomService
from app.infrastructure.database.models import Room


@pytest.fixture
def mock_room_repository():
    """Create mock room repository."""
    return AsyncMock()


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
            name="Study-Session-123",
            work_duration=1500,
            break_duration=300,
        )

        mock_room_repository.get_by_name.return_value = None

        created_room = Room(
            id=str(uuid4()),
            name="Study-Session-123",
            work_duration=25,
            break_duration=5,
            auto_start_break=True,
            is_active=True,
            host_id=user_id,
            remove_on_leave=False
        )
        created_room.created_at = datetime.now(UTC)
        created_room.updated_at = datetime.now(UTC)

        mock_room_repository.create.return_value = created_room

        result = await room_service.create_room(room_data, user_id)

        assert result is not None
        assert result.name == "Study-Session-123"
        assert result.host_id == user_id
        mock_room_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_rooms(self, room_service, mock_room_repository):
        """Test getting all active rooms."""
        room1 = Room(
            id=str(uuid4()), name="Room 1", work_duration=25, break_duration=5,
            auto_start_break=True, is_active=True, host_id=None, remove_on_leave=False
        )
        room1.created_at = datetime.now(UTC)
        room1.updated_at = datetime.now(UTC)

        room2 = Room(
            id=str(uuid4()), name="Room 2", work_duration=25, break_duration=5,
            auto_start_break=True, is_active=True, host_id=None, remove_on_leave=False
        )
        room2.created_at = datetime.now(UTC)
        room2.updated_at = datetime.now(UTC)

        mock_room_repository.get_all_active.return_value = [room1, room2]

        result = await room_service.get_all_rooms()

        assert len(result) == 2
        assert all(room.is_active is True for room in result)


def test_room_service_import():
    """Test that room service can be imported."""
    from app.domain.room.service import RoomService
    assert RoomService is not None
