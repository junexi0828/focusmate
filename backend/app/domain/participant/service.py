"""Participant domain service."""

from datetime import UTC, datetime

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
from app.infrastructure.database.models import Participant
from app.infrastructure.repositories.participant_repository import ParticipantRepository
from app.infrastructure.repositories.room_repository import RoomRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.shared.constants.timer import MAX_PARTICIPANTS_PER_ROOM
from app.shared.utils.uuid import generate_uuid


class ParticipantService:
    """Participant business logic service."""

    def __init__(
        self,
        participant_repo: ParticipantRepository,
        room_repo: RoomRepository,
        user_repo: UserRepository | None = None,
    ) -> None:
        """Initialize service."""
        self.participant_repo = participant_repo
        self.room_repo = room_repo
        self.user_repo = user_repo

    async def join_room(self, room_id: str, data: ParticipantJoin) -> ParticipantResponse:
        """Add participant to room or reconnect existing participant.

        Args:
            room_id: Room identifier
            data: Join data

        Returns:
            Created or updated participant

        Raises:
            RoomNotFoundException: If room not found
            RoomFullException: If room at capacity
        """
        # Verify room exists
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException(room_id)

        # Get username from user info if user_id is provided
        final_username = data.username
        if data.user_id and self.user_repo:
            try:
                user = await self.user_repo.get_by_id(data.user_id)
                if user:
                    # Use user's username if available, otherwise fall back to provided username
                    final_username = user.username or data.username
            except Exception:
                # If user lookup fails, use provided username
                pass

        # Check if user already has a participant record in this room
        # Use get_by_user_id_and_room_id if available, otherwise filter manually
        existing_participants = await self.participant_repo.get_by_user_id(data.user_id, active_only=False)
        existing_participant = next(
            (p for p in existing_participants if p.room_id == room_id),
            None
        )

        if existing_participant:
            # Reconnect existing participant and update user info
            existing_participant.is_connected = True
            existing_participant.left_at = None
            # Always update username from user info to ensure it's current
            existing_participant.username = final_username
            # Update user_id if it was missing
            if not existing_participant.user_id and data.user_id:
                existing_participant.user_id = data.user_id
            updated = await self.participant_repo.update(existing_participant)
            return ParticipantResponse.model_validate(updated)

        # Check room capacity (only for new participants)
        active_count = await self.participant_repo.count_active_participants(room_id)
        if active_count >= MAX_PARTICIPANTS_PER_ROOM:
            raise RoomFullException(room_id, MAX_PARTICIPANTS_PER_ROOM)

        # Check if this is the first participant (becomes host)
        is_host = active_count == 0

        # Create new participant
        participant = Participant(
            id=generate_uuid(),
            room_id=room_id,
            user_id=data.user_id,
            username=final_username,  # Use username from user info or provided
            is_connected=True,
            is_host=is_host,
            joined_at=datetime.now(UTC),
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
