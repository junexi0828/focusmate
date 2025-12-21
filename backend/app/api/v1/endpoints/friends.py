"""Friend API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from app.domain.friend.presence_service import PresenceService
from app.domain.friend.schemas import (
    FriendListResponse,
    FriendPresence,
    FriendRequestCreate,
    FriendRequestResponse,
    FriendSearchParams,
)
from app.domain.friend.service import FriendService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.friend_repository import (
    FriendRepository,
    FriendRequestRepository,
)
from app.infrastructure.repositories.presence_repository import PresenceRepository


router = APIRouter(prefix="/friends", tags=["friends"])


# Dependency Injection
def get_friend_request_repository(db: DatabaseSession) -> FriendRequestRepository:
    """Get friend request repository."""
    return FriendRequestRepository(db)


def get_friend_repository(db: DatabaseSession) -> FriendRepository:
    """Get friend repository."""
    return FriendRepository(db)


def get_presence_repository(db: DatabaseSession) -> PresenceRepository:
    """Get presence repository."""
    return PresenceRepository(db)


def get_friend_service(
    friend_request_repo: Annotated[
        FriendRequestRepository, Depends(get_friend_request_repository)
    ],
    friend_repo: Annotated[FriendRepository, Depends(get_friend_repository)],
    presence_repo: Annotated[PresenceRepository, Depends(get_presence_repository)],
) -> FriendService:
    """Get friend service."""
    return FriendService(friend_request_repo, friend_repo, presence_repo)


def get_presence_service(
    presence_repo: Annotated[PresenceRepository, Depends(get_presence_repository)],
    friend_repo: Annotated[FriendRepository, Depends(get_friend_repository)],
) -> PresenceService:
    """Get presence service."""
    return PresenceService(presence_repo, friend_repo)


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


# Presence Endpoints
@router.get("/presence", response_model=list[FriendPresence])
async def get_friends_presence(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[PresenceService, Depends(get_presence_service)],
) -> list[FriendPresence]:
    """Get presence information for all friends.

    Returns:
        List of friend presence information
    """
    return await service.get_friends_presence(current_user["id"])


@router.get("/{friend_id}/presence", response_model=FriendPresence)
async def get_friend_presence(
    friend_id: str,
    service: Annotated[PresenceService, Depends(get_presence_service)],
) -> FriendPresence:
    """Get presence for a specific friend.

    Args:
        friend_id: Friend's user ID
        service: Presence service

    Returns:
        Friend presence information

    Raises:
        HTTPException: If friend not found
    """
    presence = await service.get_user_presence(friend_id)
    if not presence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presence information not found"
        )
    return presence


# Search and Filter Endpoints
@router.get("/search", response_model=FriendListResponse)
async def search_friends(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
    query: str = Query(None, description="Search query for friend username"),
    filter_type: str = Query("all", description="Filter type: all, online, blocked"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
) -> FriendListResponse:
    """Search and filter friends.

    Args:
        current_user: Current authenticated user
        service: Friend service
        query: Search query
        filter_type: Filter type
        limit: Max results

    Returns:
        List of matching friends
    """
    params = FriendSearchParams(
        query=query,
        filter_type=filter_type,
        limit=limit,
    )
    return await service.search_friends(current_user["id"], params)


# Quick Chat Endpoint
@router.post("/{friend_id}/chat")
async def create_friend_chat(
    friend_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[FriendService, Depends(get_friend_service)],
) -> dict:
    """Create or get direct chat with a friend.

    This endpoint validates friendship and returns friend/user IDs.
    The actual chat room creation is handled by the chat service.

    Args:
        friend_id: Friend's user ID
        current_user: Current authenticated user
        service: Friend service

    Returns:
        Friend chat information

    Raises:
        HTTPException: If friendship not found or blocked
    """
    try:
        return await service.create_friend_chat(current_user["id"], friend_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
