"""Room domain service (business logic)."""

from app.core.exceptions import (
    RoomHostRequiredException,
    RoomNameTakenException,
    RoomNotFoundException,
)
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

    async def create_room(self, data: RoomCreate, user_id: str | None = None) -> RoomResponse:
        """Create a new room.

        Args:
            data: Room creation data
            user_id: Optional user ID to set as host

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
        # Convert seconds to minutes (frontend sends in seconds, Room model stores in minutes)
        room = Room(
            id=generate_uuid(),
            name=data.name,
            work_duration=data.work_duration // 60,  # Convert seconds to minutes
            break_duration=data.break_duration // 60,  # Convert seconds to minutes
            auto_start_break=data.auto_start_break,
            is_active=True,
            host_id=user_id,  # Set host_id if provided
            remove_on_leave=getattr(data, "remove_on_leave", False),  # Default to False (keep participants visible)
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

    async def update_room(
        self, room_id: str, data: RoomUpdate, user_id: str | None = None
    ) -> RoomResponse:
        """Update room settings.

        Args:
            room_id: Room identifier
            data: Update data
            user_id: User ID requesting the update (for host check)

        Returns:
            Updated room response

        Raises:
            RoomNotFoundException: If room not found
            RoomHostRequiredException: If user is not the room host
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Check host permission if user_id is provided
        if user_id is not None:
            if room.host_id is None:
                # If room has no host, allow update (backward compatibility)
                pass
            elif room.host_id != user_id:
                raise RoomHostRequiredException(room_id)

        # Update fields (convert seconds to minutes)
        work_duration_changed = False
        break_duration_changed = False

        if data.work_duration is not None:
            new_work_duration = data.work_duration // 60  # Convert seconds to minutes
            if room.work_duration != new_work_duration:
                room.work_duration = new_work_duration
                work_duration_changed = True
        if data.break_duration is not None:
            new_break_duration = data.break_duration // 60  # Convert seconds to minutes
            if room.break_duration != new_break_duration:
                room.break_duration = new_break_duration
                break_duration_changed = True
        if data.auto_start_break is not None:
            room.auto_start_break = data.auto_start_break
        if data.remove_on_leave is not None:
            room.remove_on_leave = data.remove_on_leave

        updated_room = await self.repository.update(room)

        # Update timer if duration changed
        if work_duration_changed or break_duration_changed:
            try:
                from app.domain.timer.service import TimerService
                from app.infrastructure.database.session import get_db
                from app.infrastructure.repositories.timer_repository import TimerRepository

                # Get timer repository and service
                async for db in get_db():
                    timer_repo = TimerRepository(db)
                    timer_service = TimerService(timer_repo, self.repository)

                    # Update timer durations
                    timer = await timer_repo.get_by_room_id(room_id)
                    if timer:
                        # Update duration based on current phase
                        if timer.phase == "work" and work_duration_changed:
                            # If timer is running, adjust remaining_seconds proportionally
                            if timer.status == "running" and timer.duration > 0:
                                # Calculate new remaining_seconds based on ratio
                                ratio = (room.work_duration * 60) / timer.duration
                                timer.remaining_seconds = int(timer.remaining_seconds * ratio)
                            timer.duration = room.work_duration * 60
                            timer.remaining_seconds = min(timer.remaining_seconds, room.work_duration * 60)
                        elif timer.phase == "break" and break_duration_changed:
                            # If timer is running, adjust remaining_seconds proportionally
                            if timer.status == "running" and timer.duration > 0:
                                # Calculate new remaining_seconds based on ratio
                                ratio = (room.break_duration * 60) / timer.duration
                                timer.remaining_seconds = int(timer.remaining_seconds * ratio)
                            timer.duration = room.break_duration * 60
                            timer.remaining_seconds = min(timer.remaining_seconds, room.break_duration * 60)
                        elif timer.status == "idle":
                            # If idle, update duration for next phase
                            if timer.phase == "work" and work_duration_changed:
                                timer.duration = room.work_duration * 60
                                timer.remaining_seconds = room.work_duration * 60
                            elif timer.phase == "break" and break_duration_changed:
                                timer.duration = room.break_duration * 60
                                timer.remaining_seconds = room.break_duration * 60

                        await timer_repo.update(timer)
                    break
            except Exception as e:
                # Log error but don't fail room update
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to update timer after room duration change: {e}")

        return RoomResponse.model_validate(updated_room)

    async def get_all_rooms(self) -> list[RoomResponse]:
        """Get all active rooms.

        Returns:
            List of active rooms
        """
        rooms = await self.repository.get_all_active()
        return [RoomResponse.model_validate(room) for room in rooms]

    async def delete_room(self, room_id: str, user_id: str | None = None) -> None:
        """Delete (deactivate) a room.

        Args:
            room_id: Room identifier
            user_id: User ID requesting the deletion (for host check)

        Raises:
            RoomNotFoundException: If room not found
            RoomHostRequiredException: If user is not the room host
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Check host permission if user_id is provided
        if user_id is not None:
            if room.host_id is None:
                # If room has no host, allow deletion (backward compatibility)
                pass
            elif room.host_id != user_id:
                raise RoomHostRequiredException(room_id)

        # Soft delete: set is_active to False
        room.is_active = False
        await self.repository.update(room)
