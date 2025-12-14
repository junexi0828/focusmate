"""Room Reservation API endpoints."""

from typing import Annotated

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


@router.post("/", response_model=RoomReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    data: RoomReservationCreate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
) -> RoomReservationResponse:
    """Create a new room reservation."""
    try:
        return await service.create_reservation(current_user["id"], data)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming reservations: {str(e)}"
        )


@router.put("/{reservation_id}", response_model=RoomReservationResponse)
async def update_reservation(
    reservation_id: str,
    data: RoomReservationUpdate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[RoomReservationService, Depends(get_room_reservation_service)],
) -> RoomReservationResponse:
    """Update a reservation."""
    try:
        return await service.update_reservation(reservation_id, current_user["id"], data)
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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

