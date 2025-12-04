"""Participant API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_room_repository, get_timer_repository
from app.core.exceptions import ParticipantNotFoundException, RoomFullException, RoomNotFoundException
from app.domain.participant.schemas import ParticipantJoin, ParticipantListResponse, ParticipantResponse
from app.domain.participant.service import ParticipantService
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.database.session import DatabaseSession

router = APIRouter(prefix="/participants", tags=["participants"])


def get_participant_repository(db: DatabaseSession) -> ParticipantRepository:
    """Get participant repository."""
    return ParticipantRepository(db)


def get_participant_service(
    participant_repo: Annotated[ParticipantRepository, Depends(get_participant_repository)],
    room_repo: Annotated[RoomRepository, Depends(get_room_repository)],
) -> ParticipantService:
    """Get participant service."""
    return ParticipantService(participant_repo, room_repo)


@router.post("/{room_id}/join", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def join_room(
    room_id: str,
    data: ParticipantJoin,
    service: Annotated[ParticipantService, Depends(get_participant_service)],
) -> ParticipantResponse:
    """Join a room as a participant.
    
    First participant becomes the room host.
    """
    try:
        return await service.join_room(room_id, data)
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except RoomFullException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(
    participant_id: str,
    service: Annotated[ParticipantService, Depends(get_participant_service)],
) -> None:
    """Leave a room."""
    try:
        await service.leave_room(participant_id)
    except ParticipantNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/{room_id}", response_model=ParticipantListResponse)
async def get_participants(
    room_id: str,
    service: Annotated[ParticipantService, Depends(get_participant_service)],
) -> ParticipantListResponse:
    """Get all active participants in a room."""
    return await service.get_participants(room_id)
