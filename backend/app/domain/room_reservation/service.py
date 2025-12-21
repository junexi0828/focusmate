"""Room Reservation domain service."""

from datetime import UTC, datetime

from app.core.exceptions import NotFoundException
from app.domain.room_reservation.schemas import (
    RecurrenceType,
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
        if data.scheduled_at <= datetime.now(UTC):
            raise ValueError("Scheduled time must be in the future")

        # Normalize recurrence_type (handle both Enum and string)
        recurrence_type_value = (
            data.recurrence_type.value
            if isinstance(data.recurrence_type, RecurrenceType)
            else str(data.recurrence_type)
            if data.recurrence_type
            else "none"
        )

        # Create main reservation
        reservation = RoomReservation(
            id=generate_uuid(),
            user_id=user_id,
            scheduled_at=data.scheduled_at,
            work_duration=data.work_duration,
            break_duration=data.break_duration,
            description=data.description,
            is_active=True,
            is_completed=False,
            recurrence_type=recurrence_type_value,
            recurrence_end_date=data.recurrence_end_date,
            notification_minutes=data.notification_minutes or 5,
            notification_sent=False,
        )

        created = await self.repository.create(reservation)

        # Create recurring reservations if specified
        if data.recurrence_type and data.recurrence_type.value != "none" and data.recurrence_end_date:
            await self._create_recurring_reservations(user_id, data, created.scheduled_at)

        return RoomReservationResponse.model_validate(created)

    async def _create_recurring_reservations(
        self, user_id: str, data: RoomReservationCreate, start_date: datetime
    ) -> None:
        """Create recurring reservations based on recurrence type.

        Args:
            user_id: User identifier
            data: Original reservation data
            start_date: Starting date for recurrence
        """
        from datetime import timedelta

        from app.infrastructure.database.models.room_reservation import RoomReservation

        current_date = start_date
        delta_map = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "monthly": timedelta(days=30),  # Approximate
        }

        # Normalize recurrence_type (handle both Enum and string)
        recurrence_type_str = (
            data.recurrence_type.value
            if isinstance(data.recurrence_type, RecurrenceType)
            else str(data.recurrence_type)
            if data.recurrence_type
            else "none"
        )

        delta = delta_map.get(recurrence_type_str)
        if not delta:
            return

        while current_date < data.recurrence_end_date:
            current_date += delta
            if current_date >= data.recurrence_end_date:
                break

            # Normalize recurrence_type for recurring reservations
            recurrence_type_value = (
                data.recurrence_type.value
                if isinstance(data.recurrence_type, RecurrenceType)
                else str(data.recurrence_type)
                if data.recurrence_type
                else "none"
            )

            recurring_reservation = RoomReservation(
                id=generate_uuid(),
                user_id=user_id,
                scheduled_at=current_date,
                work_duration=data.work_duration,
                break_duration=data.break_duration,
                description=data.description,
                is_active=True,
                is_completed=False,
                recurrence_type=recurrence_type_value,
                recurrence_end_date=None,  # Only main reservation has end date
                notification_minutes=data.notification_minutes or 5,
                notification_sent=False,
            )

            await self.repository.create(recurring_reservation)

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

        if data.scheduled_at and data.scheduled_at <= datetime.now(UTC):
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

    async def get_due_reservations(self) -> list[RoomReservationResponse]:
        """Get reservations that are due to be processed (within 1 minute).

        Returns:
            List of reservations that need room creation
        """
        from datetime import timedelta

        now = datetime.now(UTC)
        target_time = now + timedelta(minutes=1)

        reservations = await self.repository.get_due_reservations(now, target_time)
        return [RoomReservationResponse.model_validate(r) for r in reservations]

    async def create_room_for_reservation(
        self, reservation_id: str
    ) -> str:
        """Create a room for a reservation.

        Args:
            reservation_id: Reservation identifier

        Returns:
            Created room ID

        Raises:
            NotFoundException: If reservation not found
        """
        from app.infrastructure.database.models.room import Room
        from app.infrastructure.repositories.room_repository import RoomRepository

        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise NotFoundException(f"Reservation {reservation_id} not found")

        # Create room
        room = Room(
            id=generate_uuid(),
            name=f"Reservation {reservation.id[:8]}",
            max_participants=1,
            is_active=True,
            created_by_user_id=reservation.user_id,
        )

        # Get room repository and create room
        room_repo = RoomRepository(self.repository.session)
        created_room = await room_repo.create(room)

        # Update reservation with room_id
        reservation.room_id = created_room.id
        await self.repository.update(reservation)

        return created_room.id

    async def mark_notification_sent(self, reservation_id: str) -> bool:
        """Mark notification as sent for a reservation.

        Args:
            reservation_id: Reservation identifier

        Returns:
            True if updated successfully
        """
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            return False

        reservation.notification_sent = True
        await self.repository.update(reservation)
        return True

    async def get_reservations_needing_notification(
        self
    ) -> list[RoomReservationResponse]:
        """Get reservations that need notification sent.

        Returns:
            List of reservations needing notification
        """
        from datetime import timedelta

        reservations = await self.repository.get_reservations_needing_notification()

        # Filter reservations based on notification_minutes
        now = datetime.now(UTC)
        filtered = []
        for r in reservations:
            notification_time = r.scheduled_at - timedelta(minutes=r.notification_minutes)
            if now >= notification_time and not r.notification_sent:
                filtered.append(r)

        return [RoomReservationResponse.model_validate(r) for r in filtered]

