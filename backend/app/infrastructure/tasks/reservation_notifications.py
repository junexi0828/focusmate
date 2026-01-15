"""Background worker to send reservation reminder notifications."""

import asyncio
import logging
from datetime import UTC

from app.domain.notification.schemas import NotificationCreate
from app.domain.notification.service import NotificationService
from app.domain.room_reservation.service import RoomReservationService
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.notification_repository import NotificationRepository
from app.infrastructure.repositories.room_reservation_repository import (
    RoomReservationRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.user_settings_repository import UserSettingsRepository


logger = logging.getLogger(__name__)


class ReservationNotificationWorker:
    """Periodic worker to send reservation reminder notifications."""

    def __init__(self, interval_seconds: int = 60) -> None:
        self.interval_seconds = interval_seconds
        self.running = False

    async def start(self) -> None:
        """Start the worker loop."""
        self.running = True
        logger.info("🔔 Reservation Notification Worker started")
        while self.running:
            await self._run_once()
            await asyncio.sleep(self.interval_seconds)

    async def _run_once(self) -> None:
        """Process reservations needing notifications."""

        # Distributed coordination via Redis to prevent duplicate processing
        try:
            import redis.asyncio as aioredis
            from app.core.config import settings

            # Using a very short connection just for the lock check
            # In a production app, we might want to maintain a persistent connection pool
            redis = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )

            # Try to acquire a lock for this interval (55s TTL for 60s interval)
            # set(nx=True) ensures only one worker gets true
            lock_acquired = await redis.set("reservation_worker:lock", "locked", ex=55, nx=True)
            await redis.close()

            if not lock_acquired:
                # logger.debug("Skipping reservation check (handled by another worker)")
                return

        except Exception as e:
            logger.warning(f"Redis distributed lock check failed, proceeding cautiously: {e}")

        # Step 1: Fetch reservations needing notification (Read-only session)
        reservation_ids = []
        async for db in get_db():
            try:
                reservation_repo = RoomReservationRepository(db)
                reservation_service = RoomReservationService(reservation_repo)
                reservations = await reservation_service.get_reservations_needing_notification()

                if reservations:
                    reservation_ids = [r.id for r in reservations]
            except Exception as e:
                logger.error("Reservation notification fetch failed: %s", e, exc_info=True)
            finally:
                break

        if not reservation_ids:
            return

        # Step 2: Process each reservation in its own transaction
        # This prevents one failure from rolling back others (which would cause duplicate notifications)
        for reservation_id in reservation_ids:
            async for db in get_db():
                try:
                    # Re-initialize repos for this session
                    reservation_repo = RoomReservationRepository(db)
                    reservation_service = RoomReservationService(reservation_repo)
                    notification_service = NotificationService(
                        NotificationRepository(db),
                        UserSettingsRepository(db),
                        UserRepository(db),
                    )

                    # Re-fetch reservation
                    reservation = await reservation_repo.get_by_id(reservation_id)
                    if not reservation or reservation.is_notification_sent:
                        continue

                    scheduled_time = reservation.scheduled_at.astimezone(UTC).strftime("%m/%d %H:%M")
                    notification_data = NotificationCreate(
                        user_id=reservation.user_id,
                        type="reservation",
                        title="방 예약 알림",
                        message=f"{scheduled_time} 예약이 곧 시작됩니다.",
                        data={
                            "routing": {
                                "type": "route",
                                "path": "/reservations",
                            },
                            "reservation_id": reservation.id,
                        },
                    )
                    await notification_service.create_notification(notification_data)
                    await reservation_service.mark_notification_sent(reservation.id)

                except Exception as notify_error:
                    logger.error(
                        "Failed to send reservation notification for %s: %s",
                        reservation_id,
                        notify_error,
                    )
                # No finally block needed - get_db context manager handles commit/rollback/close
                break

    async def stop(self) -> None:
        """Stop the worker loop."""
        self.running = False
        logger.info("🛑 Reservation Notification Worker stopped")


reservation_notification_worker = ReservationNotificationWorker()
