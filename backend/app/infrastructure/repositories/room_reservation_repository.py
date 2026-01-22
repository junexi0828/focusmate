"""Room Reservation Repository.

Handles database operations for room reservations.
"""


from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.room_reservation import RoomReservation
from app.infrastructure.database.session import DatabaseSession
from datetime import UTC, datetime


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

    async def get_by_id(self, reservation_id: str) -> RoomReservation | None:
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
        now = datetime.now(UTC)
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

    async def get_due_reservations(
        self, start_time: datetime, end_time: datetime
    ) -> list[RoomReservation]:
        """Get reservations due between start and end time.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of reservations due in the time range
        """
        result = await self.session.execute(
            select(RoomReservation)
            .where(RoomReservation.is_active == True)
            .where(RoomReservation.is_completed == False)
            .where(RoomReservation.room_id.is_(None))  # Not yet processed
            .where(RoomReservation.scheduled_at >= start_time)
            .where(RoomReservation.scheduled_at <= end_time)
            .order_by(RoomReservation.scheduled_at.asc())
        )
        return list(result.scalars().all())

    async def get_reservations_needing_notification(
        self
    ) -> list[RoomReservation]:
        """Get reservations that need notification sent.

        Returns:
            List of active reservations that haven't sent notification yet
        """
        now = datetime.now(UTC)
        result = await self.session.execute(
            select(RoomReservation)
            .where(RoomReservation.is_active == True)
            .where(RoomReservation.is_completed == False)
            .where(RoomReservation.notification_sent == False)
            .where(RoomReservation.notification_minutes > 0)
            .where(RoomReservation.scheduled_at >= now)
            .order_by(RoomReservation.scheduled_at.asc())
        )
        return list(result.scalars().all())

    async def has_overlap(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_id: str | None = None,
    ) -> bool:
        """Check if user has any overlapping active reservations.

        Args:
            user_id: User identifier
            start_time: Start of the new reservation
            end_time: End of the new reservation
            exclude_id: Reservation ID to exclude (for updates)

        Returns:
            True if overlap exists
        """
        from datetime import timedelta
        # Calculate duration in minutes for database query if needed,
        # but since we store seconds, we might need a more complex query
        # or just fetch candidates.
        # However, SQL alchemy expression for (start + duration) is complex across DBs.
        # A simpler robust way for now:
        # Overlap condition: (StartA < EndB) and (EndA > StartB)
        # Here A is existing, B is new.
        # Existing End = scheduled_at + work_duration + break_duration (seconds)

        # Since we can't easily do date math in generic SQL with seconds stored as int,
        # we can fetch upcoming reservations for the user and check in python
        # OR use specific dialect functions.
        # For compatibility and simplicity given expected volume per user, checking in Python
        # after fetching "nearby" reservations is safe, OR we assume PostgreSQL calls.

        # Let's use a Python check for now which is safer for this codebase's complexity level
        # Fetch user's active reservations around the time.
        # Optimization: Fetch only for the specific day?
        # Let's fetch all active upcoming or recent valid ones.

        # A "safer" SQL approach might be to just get all active future reservations for user
        # and checking overlap in memory. Users won't have thousands of active future reservations.

        query = select(RoomReservation).where(
            RoomReservation.user_id == user_id,
            RoomReservation.is_active == True,
            RoomReservation.is_completed == False,
        )

        if exclude_id:
            query = query.where(RoomReservation.id != exclude_id)

        result = await self.session.execute(query)
        reservations = result.scalars().all()

        for res in reservations:
            # existing range
            res_start = res.scheduled_at
            res_duration_sec = res.work_duration + res.break_duration
            res_end = res_start + timedelta(seconds=res_duration_sec)

            # check overlap: (StartA < EndB) and (EndA > StartB)
            if res_start < end_time and res_end > start_time:
                return True

        return False

