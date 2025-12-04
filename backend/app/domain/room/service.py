"""Room domain service (business logic)."""

from app.core.exceptions import RoomNameTakenException, RoomNotFoundException
from app.domain.room.schemas import RoomCreate, RoomResponse, RoomUpdate
from app.infrastructure.database.models import Room
from app.infrastructure.repositories.room_repository import RoomRepository
from app.shared.utils.uuid import generate_uuid


class RoomService:
    """Room business logic service."""

    def __init__(self, repository: RoomRepository) -> None:
        """Initialize service.

        Args:
            repository: Room repository
        """
        self.repository = repository

    async def create_room(self, data: RoomCreate) -> RoomResponse:
        """Create a new room.

        Args:
            data: Room creation data

        Returns:
            Created room response

        Raises:
            RoomNameTakenException: If room name already exists
        """
        # Check if name is taken
        existing = await self.repository.get_by_name(data.name)
        if existing:
            raise RoomNameTakenException(data.name)

        # Create room
        room = Room(
            id=generate_uuid(),
            name=data.name,
            work_duration=data.work_duration,
            break_duration=data.break_duration,
            auto_start_break=data.auto_start_break,
            is_active=True,
        )

        created_room = await self.repository.create(room)
        return RoomResponse.model_validate(created_room)

    async def get_room(self, room_id: str) -> RoomResponse:
        """Get room by ID.

        Args:
            room_id: Room identifier

        Returns:
            Room response

        Raises:
            RoomNotFoundException: If room not found
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)
        return RoomResponse.model_validate(room)

    async def update_room(self, room_id: str, data: RoomUpdate) -> RoomResponse:
        """Update room settings.

        Args:
            room_id: Room identifier
            data: Update data

        Returns:
            Updated room response

        Raises:
            RoomNotFoundException: If room not found
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Update fields
        if data.work_duration is not None:
            room.work_duration = data.work_duration
        if data.break_duration is not None:
            room.break_duration = data.break_duration
        if data.auto_start_break is not None:
            room.auto_start_break = data.auto_start_break

        updated_room = await self.repository.update(room)
        return RoomResponse.model_validate(updated_room)

    async def get_all_rooms(self) -> list[RoomResponse]:
        """Get all active rooms.

        Returns:
            List of active rooms
        """
        rooms = await self.repository.get_all_active()
        return [RoomResponse.model_validate(room) for room in rooms]

    async def delete_room(self, room_id: str) -> None:
        """Delete (deactivate) a room.

        Args:
            room_id: Room identifier

        Raises:
            RoomNotFoundException: If room not found
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Soft delete: set is_active to False
        room.is_active = False
        await self.repository.update(room)
