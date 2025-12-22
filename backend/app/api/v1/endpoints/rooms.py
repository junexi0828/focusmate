"""Room API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user_required, get_room_service
from app.core.exceptions import (
    RoomHostRequiredException,
    RoomNameTakenException,
    RoomNotFoundException,
)
from app.domain.room.schemas import RoomCreate, RoomResponse, RoomUpdate
from app.domain.room.service import RoomService
from app.infrastructure.database.session import DatabaseSession


router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=list[RoomResponse])
async def list_rooms(
    service: Annotated[RoomService, Depends(get_room_service)],
) -> list[RoomResponse]:
    """List all active rooms."""
    return await service.get_all_rooms()


@router.get("/my-rooms", response_model=list[RoomResponse])
async def get_my_rooms(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    db: DatabaseSession,
    service: Annotated[RoomService, Depends(get_room_service)],
) -> list[RoomResponse]:
    """Get rooms that the current user is participating in."""
    try:
        from app.infrastructure.repositories.participant_repository import (
            ParticipantRepository,
        )

        participant_repo = ParticipantRepository(db)

        # Get all participants for this user
        # If room has remove_on_leave=True, only show active participants
        # If room has remove_on_leave=False, show all participants (including disconnected)
        all_participants = await participant_repo.get_by_user_id(current_user["id"], active_only=False)

        # Get unique room IDs
        room_ids = list(set([p.room_id for p in all_participants]))

        # Get rooms and filter based on remove_on_leave setting
        rooms = []
        for room_id in room_ids:
            try:
                room = await service.get_room(room_id)
                if not room:
                    continue

                # If room has remove_on_leave=True, only include if participant is active
                if room.remove_on_leave:
                    # Check if user has an active participant in this room
                    active_participant = next(
                        (p for p in all_participants if p.room_id == room_id and p.is_connected),
                        None
                    )
                    if active_participant:
                        rooms.append(room)
                else:
                    # If remove_on_leave=False, include room regardless of connection status
                    rooms.append(room)
            except (ValueError, AttributeError, KeyError) as e:
                # Skip rooms with invalid data or missing relationships
                # Log for debugging but continue processing other rooms
                continue

        return rooms
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rooms: {e!s}"
        )


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    db: DatabaseSession,
    service: Annotated[RoomService, Depends(get_room_service)],
) -> RoomResponse:
    """Create a new room and automatically add creator as participant."""
    try:
        # Create room with host_id
        room = await service.create_room(data, user_id=current_user["id"])

        # Automatically add creator as participant (host)
        from app.domain.participant.schemas import ParticipantJoin
        from app.domain.participant.service import ParticipantService
        from app.domain.timer.service import TimerService
        from app.infrastructure.repositories.participant_repository import (
            ParticipantRepository,
        )
        from app.infrastructure.repositories.room_repository import RoomRepository
        from app.infrastructure.repositories.timer_repository import TimerRepository
        from app.infrastructure.repositories.user_repository import UserRepository

        participant_repo = ParticipantRepository(db)
        room_repo = RoomRepository(db)
        user_repo = UserRepository(db)
        participant_service = ParticipantService(participant_repo, room_repo, user_repo)

        # Add creator as participant (will become host if first participant)
        await participant_service.join_room(
            room.id,
            ParticipantJoin(
                user_id=current_user["id"],
                username=current_user.get("username", current_user.get("email", "User")),
            ),
        )

        # Create timer for the room if it doesn't exist
        timer_repo = TimerRepository(db)
        timer_service = TimerService(timer_repo, room_repo)
        await timer_service.get_or_create_timer(room.id)

        return room
    except RoomNameTakenException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: str,
    service: Annotated[RoomService, Depends(get_room_service)],
) -> RoomResponse:
    """Get room by ID."""
    try:
        return await service.get_room(room_id)
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    data: RoomUpdate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    db: DatabaseSession,
    service: Annotated[RoomService, Depends(get_room_service)],
) -> RoomResponse:
    """Update room settings. Only the room host can update settings."""
    try:
        # Get current room to check if durations changed
        from app.infrastructure.repositories.room_repository import RoomRepository
        room_repo = RoomRepository(db)
        current_room = await room_repo.get_by_id(room_id)
        if not current_room:
            raise RoomNotFoundException(room_id)

        old_work_duration = current_room.work_duration
        old_break_duration = current_room.break_duration

        # Update room
        updated_room = await service.update_room(room_id, data, user_id=current_user["id"])

        # Check if durations changed
        work_duration_changed = (
            data.work_duration is not None and
            (data.work_duration // 60) != old_work_duration
        )
        break_duration_changed = (
            data.break_duration is not None and
            (data.break_duration // 60) != old_break_duration
        )

        # Update timer if durations changed
        if work_duration_changed or break_duration_changed:
            try:
                from app.domain.timer.service import TimerService
                from app.infrastructure.repositories.timer_repository import TimerRepository

                timer_repo = TimerRepository(db)
                timer_service = TimerService(timer_repo, room_repo)

                # Get timer
                timer = await timer_repo.get_by_room_id(room_id)
                if timer:
                    # Get updated room to get new durations
                    updated_room_model = await room_repo.get_by_id(room_id)
                    if updated_room_model:
                        # Update timer duration based on current phase
                        if timer.phase == "work" and work_duration_changed:
                            new_duration = updated_room_model.work_duration * 60
                            # If timer is running, adjust remaining_seconds proportionally
                            if timer.status == "running" and timer.duration > 0:
                                ratio = new_duration / timer.duration
                                timer.remaining_seconds = int(timer.remaining_seconds * ratio)
                                # Ensure remaining_seconds doesn't exceed new duration
                                timer.remaining_seconds = min(timer.remaining_seconds, new_duration)
                            timer.duration = new_duration
                            # If idle, also update remaining_seconds
                            if timer.status == "idle":
                                timer.remaining_seconds = new_duration
                        elif timer.phase == "break" and break_duration_changed:
                            new_duration = updated_room_model.break_duration * 60
                            # If timer is running, adjust remaining_seconds proportionally
                            if timer.status == "running" and timer.duration > 0:
                                ratio = new_duration / timer.duration
                                timer.remaining_seconds = int(timer.remaining_seconds * ratio)
                                # Ensure remaining_seconds doesn't exceed new duration
                                timer.remaining_seconds = min(timer.remaining_seconds, new_duration)
                            timer.duration = new_duration
                            # If idle, also update remaining_seconds
                            if timer.status == "idle":
                                timer.remaining_seconds = new_duration

                        await timer_repo.update(timer)

                        # Broadcast timer update via WebSocket
                        try:
                            from app.infrastructure.websocket.manager import connection_manager
                            await connection_manager.broadcast_to_room(
                                room_id,
                                {
                                    "type": "timer_updated",
                                    "data": {
                                        "room_id": room_id,
                                        "work_duration": updated_room_model.work_duration * 60,
                                        "break_duration": updated_room_model.break_duration * 60,
                                    },
                                },
                            )
                        except Exception as ws_error:
                            # Log but don't fail
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.warning(f"Failed to broadcast timer update: {ws_error}")
            except Exception as timer_error:
                # Log but don't fail room update
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to update timer after room duration change: {timer_error}")

        return updated_room
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except RoomHostRequiredException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[RoomService, Depends(get_room_service)],
) -> None:
    """Delete (deactivate) a room. Only the room host can delete the room."""
    try:
        await service.delete_room(room_id, user_id=current_user["id"])
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except RoomHostRequiredException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
