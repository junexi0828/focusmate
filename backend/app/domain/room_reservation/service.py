"""Room Reservation domain service."""

from datetime import datetime

from app.core.exceptions import NotFoundException
from app.domain.room_reservation.schemas import (
    RoomReservationCreate,
    RoomReservationResponse,
    RoomReservationUpdate,
)
from app.infrastructure.repositories.room_reservation_repository import (
    RoomReservationRepository,
)
from app.shared.utils.uuid import generate_uuid


class RoomReservationService:
    """Room reservation business logic."""

    def __init__(self, repository: RoomReservationRepository) -> None:
        """Initialize service.

        Args:
            repository: Room reservation repository
        """
        self.repository = repository

    async def create_reservation(
        self, user_id: str, data: RoomReservationCreate
    ) -> RoomReservationResponse:
        """Create a new room reservation.

        Args:
            user_id: User identifier
            data: Reservation data

        Returns:
            Created reservation
        """
        from app.infrastructure.database.models.room_reservation import RoomReservation

        # Validate scheduled_at is in the future
        if data.scheduled_at <= datetime.now():
            raise ValueError("Scheduled time must be in the future")

        reservation = RoomReservation(
            id=generate_uuid(),
            user_id=user_id,
            scheduled_at=data.scheduled_at,
            work_duration=data.work_duration,
            break_duration=data.break_duration,
            description=data.description,
            is_active=True,
            is_completed=False,
        )

        created = await self.repository.create(reservation)
        return RoomReservationResponse.model_validate(created)

    async def get_user_reservations(
        self, user_id: str, active_only: bool = True
    ) -> list[RoomReservationResponse]:
        """Get all reservations for a user.

        Args:
            user_id: User identifier
            active_only: Only return active reservations

        Returns:
            List of reservations
        """
        reservations = await self.repository.get_by_user_id(user_id, active_only)
        return [RoomReservationResponse.model_validate(r) for r in reservations]

    async def get_upcoming_reservations(
        self, user_id: str
    ) -> list[RoomReservationResponse]:
        """Get upcoming reservations for a user.

        Args:
            user_id: User identifier

        Returns:
            List of upcoming reservations
        """
        reservations = await self.repository.get_upcoming(user_id)
        return [RoomReservationResponse.model_validate(r) for r in reservations]

    async def update_reservation(
        self, reservation_id: str, user_id: str, data: RoomReservationUpdate
    ) -> RoomReservationResponse:
        """Update a reservation.

        Args:
            reservation_id: Reservation identifier
            user_id: User identifier (for authorization)
            data: Update data

        Returns:
            Updated reservation

        Raises:
            NotFoundException: If reservation not found
            ValueError: If user doesn't own the reservation
        """
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise NotFoundException(f"Reservation {reservation_id} not found")

        if reservation.user_id != user_id:
            raise ValueError("You can only update your own reservations")

        if data.scheduled_at and data.scheduled_at <= datetime.now():
            raise ValueError("Scheduled time must be in the future")

        if data.scheduled_at:
            reservation.scheduled_at = data.scheduled_at
        if data.work_duration is not None:
            reservation.work_duration = data.work_duration
        if data.break_duration is not None:
            reservation.break_duration = data.break_duration
        if data.description is not None:
            reservation.description = data.description

        updated = await self.repository.update(reservation)
        return RoomReservationResponse.model_validate(updated)

    async def cancel_reservation(self, reservation_id: str, user_id: str) -> bool:
        """Cancel a reservation.

        Args:
            reservation_id: Reservation identifier
            user_id: User identifier (for authorization)

        Returns:
            True if cancelled, False if not found

        Raises:
            ValueError: If user doesn't own the reservation
        """
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            return False

        if reservation.user_id != user_id:
            raise ValueError("You can only cancel your own reservations")

        return await self.repository.delete(reservation_id)

