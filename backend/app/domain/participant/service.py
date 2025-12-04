"""Participant domain service."""

from datetime import datetime, timezone

from app.core.exceptions import ParticipantNotFoundException, RoomFullException, RoomNotFoundException
from app.domain.participant.schemas import ParticipantJoin, ParticipantListResponse, ParticipantResponse
from app.infrastructure.database.models import Participant
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.infrastructure.repositories.room_repository import RoomRepository
from app.shared.constants.timer import MAX_PARTICIPANTS_PER_ROOM
from app.shared.utils.uuid import generate_uuid


class ParticipantService:
    """Participant business logic service."""

    def __init__(
        self,
        participant_repo: ParticipantRepository,
        room_repo: RoomRepository,
    ) -> None:
        """Initialize service."""
        self.participant_repo = participant_repo
        self.room_repo = room_repo

    async def join_room(self, room_id: str, data: ParticipantJoin) -> ParticipantResponse:
        """Add participant to room.
        
        Args:
            room_id: Room identifier
            data: Join data
            
        Returns:
            Created participant
            
        Raises:
            RoomNotFoundException: If room not found
            RoomFullException: If room at capacity
        """
        # Verify room exists
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Check room capacity
        active_count = await self.participant_repo.count_active_participants(room_id)
        if active_count >= MAX_PARTICIPANTS_PER_ROOM:
            raise RoomFullException(room_id, MAX_PARTICIPANTS_PER_ROOM)

        # Check if this is the first participant (becomes host)
        is_host = active_count == 0

        # Create participant
        participant = Participant(
            id=generate_uuid(),
            room_id=room_id,
            user_id=data.user_id,
            username=data.username,
            is_connected=True,
            is_host=is_host,
            joined_at=datetime.now(timezone.utc),
        )

        created = await self.participant_repo.create(participant)
        return ParticipantResponse.model_validate(created)

    async def leave_room(self, participant_id: str) -> None:
        """Remove participant from room.
        
        Args:
            participant_id: Participant identifier
            
        Raises:
            ParticipantNotFoundException: If participant not found
        """
        participant = await self.participant_repo.mark_disconnected(participant_id)
        if not participant:
            raise ParticipantNotFoundException(participant_id)

    async def get_participants(self, room_id: str) -> ParticipantListResponse:
        """Get all participants in a room.
        
        Args:
            room_id: Room identifier
            
        Returns:
            List of participants
        """
        participants = await self.participant_repo.get_by_room_id(room_id, active_only=True)
        return ParticipantListResponse(
            participants=[ParticipantResponse.model_validate(p) for p in participants],
            total=len(participants),
        )
