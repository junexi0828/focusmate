"""Friend API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException
from app.domain.friend.schemas import (
    FriendRequestCreate,
    FriendRequestResponse,
    FriendListResponse,
)
from app.domain.friend.service import FriendService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.friend_repository import (
    FriendRequestRepository,
    FriendRepository,
)

router = APIRouter(prefix="/friends", tags=["friends"])


# Dependency Injection
def get_friend_request_repository(db: DatabaseSession) -> FriendRequestRepository:
    """Get friend request repository."""
    return FriendRequestRepository(db)


def get_friend_repository(db: DatabaseSession) -> FriendRepository:
    """Get friend repository."""
    return FriendRepository(db)


def get_friend_service(
    friend_request_repo: Annotated[
        FriendRequestRepository, Depends(get_friend_request_repository)
    ],
    friend_repo: Annotated[FriendRepository, Depends(get_friend_repository)],
) -> FriendService:
    """Get friend service."""
    return FriendService(friend_request_repo, friend_repo)


# Friend Request Endpoints
@router.post("/requests", response_model=FriendRequestResponse, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    data: FriendRequestCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> FriendRequestResponse:
    """Send a friend request.

    Args:
        data: Friend request data with receiver_id
        current_user: Current authenticated user
        service: Friend service

    Returns:
        Created friend request

    Raises:
        HTTPException: If user not found or request already exists
    """
    try:
        return await service.send_friend_request(current_user["id"], data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.get("/requests/received", response_model=list[FriendRequestResponse])
async def get_received_requests(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
    pending_only: bool = Query(False, description="Only show pending requests"),
) -> list[FriendRequestResponse]:
    """Get friend requests received by current user.

    Args:
        current_user: Current authenticated user
        service: Friend service
        pending_only: Whether to show only pending requests

    Returns:
        List of friend requests
    """
    return await service.get_received_requests(current_user["id"], pending_only)


@router.get("/requests/sent", response_model=list[FriendRequestResponse])
async def get_sent_requests(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> list[FriendRequestResponse]:
    """Get friend requests sent by current user.

    Args:
        current_user: Current authenticated user
        service: Friend service

    Returns:
        List of friend requests
    """
    return await service.get_sent_requests(current_user["id"])


@router.post("/requests/{request_id}/accept", response_model=FriendRequestResponse)
async def accept_friend_request(
    request_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> FriendRequestResponse:
    """Accept a friend request.

    Args:
        request_id: Friend request identifier
        current_user: Current authenticated user
        service: Friend service

    Returns:
        Updated friend request

    Raises:
        HTTPException: If request not found or unauthorized
    """
    try:
        return await service.accept_friend_request(request_id, current_user["id"])
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.post("/requests/{request_id}/reject", response_model=FriendRequestResponse)
async def reject_friend_request(
    request_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> FriendRequestResponse:
    """Reject a friend request.

    Args:
        request_id: Friend request identifier
        current_user: Current authenticated user
        service: Friend service

    Returns:
        Updated friend request

    Raises:
        HTTPException: If request not found or unauthorized
    """
    try:
        return await service.reject_friend_request(request_id, current_user["id"])
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.delete("/requests/{request_id}", status_code=status.HTTP_200_OK)
async def cancel_friend_request(
    request_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> dict:
    """Cancel a sent friend request.

    Args:
        request_id: Friend request identifier
        current_user: Current authenticated user
        service: Friend service

    Returns:
        Cancellation confirmation

    Raises:
        HTTPException: If request not found or unauthorized
    """
    try:
        return await service.cancel_friend_request(request_id, current_user["id"])
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


# Friend Endpoints
@router.get("/", response_model=FriendListResponse)
async def get_friends(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> FriendListResponse:
    """Get all friends of current user.

    Args:
        current_user: Current authenticated user
        service: Friend service

    Returns:
        List of friends
    """
    return await service.get_friends(current_user["id"])


@router.delete("/{friend_id}", status_code=status.HTTP_200_OK)
async def remove_friend(
    friend_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> dict:
    """Remove a friend.

    Args:
        friend_id: Friend's user ID
        current_user: Current authenticated user
        service: Friend service

    Returns:
        Removal confirmation

    Raises:
        HTTPException: If friendship not found
    """
    try:
        return await service.remove_friend(current_user["id"], friend_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/{friend_id}/block", status_code=status.HTTP_200_OK)
async def block_friend(
    friend_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> dict:
    """Block a friend.

    Args:
        friend_id: Friend's user ID
        current_user: Current authenticated user
        service: Friend service

    Returns:
        Block confirmation

    Raises:
        HTTPException: If friendship not found
    """
    try:
        return await service.block_friend(current_user["id"], friend_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/{friend_id}/unblock", status_code=status.HTTP_200_OK)
async def unblock_friend(
    friend_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> dict:
    """Unblock a friend.

    Args:
        friend_id: Friend's user ID
        current_user: Current authenticated user
        service: Friend service

    Returns:
        Unblock confirmation

    Raises:
        HTTPException: If friendship not found
    """
    try:
        return await service.unblock_friend(current_user["id"], friend_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
