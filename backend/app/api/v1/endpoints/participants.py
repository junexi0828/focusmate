"""Participant API endpoints."""


from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user_required, get_room_repository
from app.core.exceptions import (
    ParticipantNotFoundException,
    RoomFullException,
    RoomNotFoundException,
)
from app.domain.participant.schemas import (
    ParticipantJoin,
    ParticipantListResponse,
    ParticipantResponse,
)
from app.domain.participant.service import ParticipantService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.user_repository import UserRepository


router = APIRouter(prefix="/participants", tags=["participants"])


def get_participant_repository(db: DatabaseSession) -> ParticipantRepository:
    """Get participant repository."""
    return ParticipantRepository(db)


def get_user_repository(db: DatabaseSession) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


def get_participant_service(
    participant_repo: Annotated[ParticipantRepository, Depends(get_participant_repository)],
    room_repo: Annotated[RoomRepository, Depends(get_room_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> ParticipantService:
    """Get participant service."""
    return ParticipantService(participant_repo, room_repo, user_repo)


@router.post("/{room_id}/join", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def join_room(
    room_id: str,
    data: ParticipantJoin,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[ParticipantService, Depends(get_participant_service)],
) -> ParticipantResponse:
    """Join a room as a participant.

    First participant becomes the room host.
    """
    try:
        join_data = ParticipantJoin(
            username=current_user.get("username")
            or current_user.get("email")
            or data.username,
            user_id=current_user["id"],
            participant_id=data.participant_id,
        )
        return await service.join_room(room_id, join_data)
    except RoomNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except RoomFullException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(
    participant_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[ParticipantService, Depends(get_participant_service)],
    participant_repo: Annotated[ParticipantRepository, Depends(get_participant_repository)],
) -> None:
    """Leave a room."""
    try:
        participant = await participant_repo.get_by_id(participant_id)
        if not participant:
            raise ParticipantNotFoundException(participant_id)
        if participant.user_id != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        await service.leave_room(participant_id)
    except ParticipantNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/{room_id}", response_model=ParticipantListResponse)
async def get_participants(
    room_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[ParticipantService, Depends(get_participant_service)],
) -> ParticipantListResponse:
    """Get all active participants in a room."""
    try:
        return await service.get_participants(room_id)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to get participants for room {room_id}: {e}", exc_info=True)
        # Re-raise as HTTPException to ensure CORS headers are added by main.py exception handler
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "PARTICIPANT_LIST_ERROR", "message": "Failed to retrieve participants"},
        )
