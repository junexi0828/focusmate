"""Room Reservation Repository.

Handles database operations for room reservations.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.room_reservation import RoomReservation
from app.infrastructure.database.session import DatabaseSession


class RoomReservationRepository:
    """Repository for room reservation operations."""

    def __init__(self, session: DatabaseSession) -> None:
        """Initialize repository.

        Args:
            session: Database session
        """
        self.session: AsyncSession = session

    async def create(self, reservation: RoomReservation) -> RoomReservation:
        """Create a new reservation.

        Args:
            reservation: Reservation to create

        Returns:
            Created reservation
        """
        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def get_by_id(self, reservation_id: str) -> Optional[RoomReservation]:
        """Get reservation by ID.

        Args:
            reservation_id: Reservation identifier

        Returns:
            Reservation if found, None otherwise
        """
        result = await self.session.execute(
            select(RoomReservation).where(RoomReservation.id == reservation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: str, active_only: bool = True
    ) -> list[RoomReservation]:
        """Get all reservations for a user.

        Args:
            user_id: User identifier
            active_only: Only return active reservations

        Returns:
            List of reservations
        """
        query = select(RoomReservation).where(RoomReservation.user_id == user_id)
        if active_only:
            query = query.where(RoomReservation.is_active == True)
        query = query.order_by(RoomReservation.scheduled_at.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_upcoming(self, user_id: str) -> list[RoomReservation]:
        """Get upcoming reservations for a user.

        Args:
            user_id: User identifier

        Returns:
            List of upcoming active reservations
        """
        now = datetime.now()
        result = await self.session.execute(
            select(RoomReservation)
            .where(RoomReservation.user_id == user_id)
            .where(RoomReservation.is_active == True)
            .where(RoomReservation.scheduled_at >= now)
            .order_by(RoomReservation.scheduled_at.asc())
        )
        return list(result.scalars().all())

    async def update(self, reservation: RoomReservation) -> RoomReservation:
        """Update a reservation.

        Args:
            reservation: Reservation to update

        Returns:
            Updated reservation
        """
        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def delete(self, reservation_id: str) -> bool:
        """Delete a reservation (soft delete by setting is_active=False).

        Args:
            reservation_id: Reservation identifier

        Returns:
            True if deleted, False if not found
        """
        reservation = await self.get_by_id(reservation_id)
        if not reservation:
            return False
        reservation.is_active = False
        await self.session.commit()
        return True

