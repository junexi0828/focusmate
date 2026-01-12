"""Room Reservation API endpoints."""

from typing import Annotated, List
from datetime import UTC, datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user_required
from app.core.exceptions import NotFoundException
from app.domain.room_reservation.schemas import (
    RoomReservationCreate,
    RoomReservationResponse,
    RoomReservationUpdate,

)
from app.domain.room_reservation.service import RoomReservationService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.room_reservation_repository import (
    RoomReservationRepository,
)
from app.domain.notification.service import NotificationService
from app.domain.notification.schemas import NotificationCreate
from app.infrastructure.repositories.notification_repository import (
    NotificationRepository,
)
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.user_settings_repository import (
    UserSettingsRepository,
)
from app.infrastructure.websocket.notification_manager import notification_ws_manager
from app.shared.utils.uuid import generate_uuid


router = APIRouter(prefix="/room-reservations", tags=["room-reservations"])


def get_room_reservation_repository(
    db: DatabaseSession,
) -> RoomReservationRepository:
    """Get room reservation repository."""
    return RoomReservationRepository(db)


def get_room_reservation_service(
    repository: Annotated[
        RoomReservationRepository, Depends(get_room_reservation_repository)
    ],
) -> RoomReservationService:
    """Get room reservation service."""
    return RoomReservationService(repository)

async def send_reservation_update(
    user_id: str,
    reservation_id: str,
    action: str,
) -> None:
    """Send reservation update event via WebSocket."""
    try:
        await notification_ws_manager.send_notification(
            {
                "type": "notification",
                "data": {
                    "notification_id": generate_uuid(),
                    "type": "reservation_update",
                    "title": "reservation_update",
                    "message": "",
                    "data": {
                        "reservation_id": reservation_id,
                        "action": action,
                    },
                    "created_at": datetime.now(UTC).isoformat(),
                },
            },
            user_id,
        )
    except Exception as e:
        logging.getLogger(__name__).warning(
            "Failed to send reservation update: %s",
            e,
        )


@router.post("/", response_model=RoomReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    data: RoomReservationCreate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
) -> RoomReservationResponse:
    """Create a new room reservation."""
    try:
        created = await service.create_reservation(current_user["id"], data)
        await send_reservation_update(current_user["id"], created.id, "created")
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[RoomReservationResponse])
async def get_my_reservations(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
    active_only: bool = True,
) -> list[RoomReservationResponse]:
    """Get all reservations for the current user."""
    return await service.get_user_reservations(current_user["id"], active_only)


@router.get("/upcoming", response_model=list[RoomReservationResponse])
async def get_upcoming_reservations(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
) -> list[RoomReservationResponse]:
    """Get upcoming reservations for the current user."""
    try:
        return await service.get_upcoming_reservations(current_user["id"])
    except Exception as e:
        # Return empty list to prevent UI crash when DB is unstable
        logging.getLogger(__name__).error(f"Failed to get upcoming reservations: {e}", exc_info=True)
        return []


@router.put("/{reservation_id}", response_model=RoomReservationResponse)
async def update_reservation(
    reservation_id: str,
    data: RoomReservationUpdate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
) -> RoomReservationResponse:
    """Update a reservation."""
    try:
        updated = await service.update_reservation(reservation_id, current_user["id"], data)
        await send_reservation_update(current_user["id"], reservation_id, "updated")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reservation(
    reservation_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
) -> None:
    """Cancel a reservation."""
    try:
        cancelled = await service.cancel_reservation(reservation_id, current_user["id"])
        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
            )
        await send_reservation_update(current_user["id"], reservation_id, "cancelled")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/process-due", response_model=dict)
async def process_due_reservations(
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
) -> dict:
    """Process reservations that are due (create rooms for them).

    This endpoint should be called by a scheduler/cron job.
    """
    try:
        due_reservations = await service.get_due_reservations()
        processed_count = 0

        for reservation in due_reservations:
            try:
                await service.create_room_for_reservation(reservation.id)
                processed_count += 1
            except Exception as e:
                # Log error but continue processing other reservations
                logging.getLogger(__name__).error(f"Error creating room for reservation {reservation.id}: {e}")

        return {
            "status": "success",
            "processed_count": processed_count,
            "total_due": len(due_reservations)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process due reservations: {e!s}"
        )


@router.post("/send-notifications", response_model=dict)
async def send_notifications(
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
) -> dict:
    """Send notifications for upcoming reservations.

    This endpoint should be called by a scheduler/cron job.
    """
    try:
        reservations = await service.get_reservations_needing_notification()
        sent_count = 0

        from app.infrastructure.database.session import get_db

        async for db in get_db():
            notification_repo = NotificationRepository(db)
            settings_repo = UserSettingsRepository(db)
            user_repo = UserRepository(db)
            notification_service = NotificationService(
                notification_repo,
                settings_repo,
                user_repo,
            )

            for reservation in reservations:
                try:
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
                    await service.mark_notification_sent(reservation.id)
                    sent_count += 1
                except Exception as e:
                    logging.getLogger(__name__).error(
                        f"Error sending notification for reservation {reservation.id}: {e}"
                    )
            break

        return {
            "status": "success",
            "sent_count": sent_count,
            "total_pending": len(reservations)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notifications: {e!s}"
        )
