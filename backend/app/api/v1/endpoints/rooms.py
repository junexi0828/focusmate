"""Room API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user_required, get_room_service
from app.core.exceptions import RoomNameTakenException, RoomNotFoundException
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
        participants = await participant_repo.get_by_user_id(current_user["id"], active_only=True)

        # Get unique room IDs
        room_ids = list(set([p.room_id for p in participants]))

        # Get rooms
        rooms = []
        for room_id in room_ids:
            try:
                room = await service.get_room(room_id)
                if room:
                    rooms.append(room)
            except Exception:
                continue

        return rooms
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rooms: {str(e)}"
        )


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    service: Annotated[RoomService, Depends(get_room_service)],
) -> RoomResponse:
    """Create a new room."""
    try:
        return await service.create_room(data)
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
    service: Annotated[RoomService, Depends(get_room_service)],
) -> RoomResponse:
    """Update room settings."""
    try:
        return await service.update_room(room_id, data)
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: str,
    service: Annotated[RoomService, Depends(get_room_service)],
) -> None:
    """Delete (deactivate) a room."""
    try:
        await service.delete_room(room_id)
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
