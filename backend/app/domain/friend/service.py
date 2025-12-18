"""Friend service."""

from typing import Optional
from uuid import uuid4

from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException
from app.domain.friend.schemas import (
    FriendRequestCreate,
    FriendRequestResponse,
    FriendResponse,
    FriendListResponse,
    FriendSearchParams,
)
from app.infrastructure.database.models.friend import FriendRequestStatus
from app.infrastructure.repositories.friend_repository import (
    FriendRequestRepository,
    FriendRepository,
)
from app.infrastructure.repositories.presence_repository import PresenceRepository


class FriendService:
    """Service for friend operations."""

    def __init__(
        self,
        friend_request_repo: FriendRequestRepository,
        friend_repo: FriendRepository,
        presence_repo: Optional[PresenceRepository] = None,
    ):
        self.friend_request_repo = friend_request_repo
        self.friend_repo = friend_repo
        self.presence_repo = presence_repo

    async def send_friend_request(
        self, sender_id: str, data: FriendRequestCreate
    ) -> FriendRequestResponse:
        """Send a friend request."""
        receiver_id = data.receiver_id

        # Check if receiver exists
        receiver = await self.friend_repo.get_user_by_id(receiver_id)
        if not receiver:
            raise NotFoundException("User not found")

        # Cannot send request to self
        if sender_id == receiver_id:
            raise ConflictException("Cannot send friend request to yourself")

        # Check if already friends
        existing_friendship = await self.friend_repo.get_friendship(sender_id, receiver_id)
        if existing_friendship:
            raise ConflictException("Already friends with this user")

        # Check for existing pending request
        existing_request = await self.friend_request_repo.get_pending_request(
            sender_id, receiver_id
        )
        if existing_request:
            raise ConflictException("Friend request already sent")

        # Check for reverse pending request
        reverse_request = await self.friend_request_repo.get_pending_request(
            receiver_id, sender_id
        )
        if reverse_request:
            raise ConflictException("This user has already sent you a friend request")

        # Create friend request
        request_id = str(uuid4())
        request = await self.friend_request_repo.create_request(
            sender_id, receiver_id, request_id
        )

        # Get sender info
        sender = await self.friend_repo.get_user_by_id(sender_id)

        return FriendRequestResponse(
            id=request.id,
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            status=request.status,
            created_at=request.created_at,
            responded_at=request.responded_at,
            sender_username=sender.username if sender else None,
            sender_profile_image=sender.profile_image if sender else None,
            receiver_username=receiver.username,
            receiver_profile_image=receiver.profile_image,
        )

    async def get_received_requests(
        self, user_id: str, pending_only: bool = False
    ) -> list[FriendRequestResponse]:
        """Get friend requests received by user."""
        requests = await self.friend_request_repo.get_user_received_requests(
            user_id, pending_only
        )

        result = []
        for request in requests:
            sender = await self.friend_repo.get_user_by_id(request.sender_id)
            result.append(
                FriendRequestResponse(
                    id=request.id,
                    sender_id=request.sender_id,
                    receiver_id=request.receiver_id,
                    status=request.status,
                    created_at=request.created_at,
                    responded_at=request.responded_at,
                    sender_username=sender.username if sender else "Unknown",
                    sender_profile_image=sender.profile_image if sender else None,
                )
            )
        return result

    async def get_sent_requests(self, user_id: str) -> list[FriendRequestResponse]:
        """Get friend requests sent by user."""
        requests = await self.friend_request_repo.get_user_sent_requests(user_id)

        result = []
        for request in requests:
            receiver = await self.friend_repo.get_user_by_id(request.receiver_id)
            result.append(
                FriendRequestResponse(
                    id=request.id,
                    sender_id=request.sender_id,
                    receiver_id=request.receiver_id,
                    status=request.status,
                    created_at=request.created_at,
                    responded_at=request.responded_at,
                    receiver_username=receiver.username if receiver else "Unknown",
                    receiver_profile_image=receiver.profile_image if receiver else None,
                )
            )
        return result

    async def accept_friend_request(
        self, request_id: str, user_id: str
    ) -> FriendRequestResponse:
        """Accept a friend request."""
        request = await self.friend_request_repo.get_request_by_id(request_id)
        if not request:
            raise NotFoundException("Friend request not found")

        # Verify user is the receiver
        if request.receiver_id != user_id:
            raise UnauthorizedException("Not authorized to accept this request")

        # Update request status
        request = await self.friend_request_repo.update_request_status(
            request_id, FriendRequestStatus.ACCEPTED
        )

        # Create friendship
        friendship_id_1 = str(uuid4())
        friendship_id_2 = str(uuid4())
        await self.friend_repo.create_friendship(
            request.sender_id, request.receiver_id, friendship_id_1, friendship_id_2
        )

        # Get sender info
        sender = await self.friend_repo.get_user_by_id(request.sender_id)

        return FriendRequestResponse(
            id=request.id,
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            status=request.status,
            created_at=request.created_at,
            responded_at=request.responded_at,
            sender_username=sender.username if sender else "Unknown",
            sender_profile_image=sender.profile_image if sender else None,
        )

    async def reject_friend_request(
        self, request_id: str, user_id: str
    ) -> FriendRequestResponse:
        """Reject a friend request."""
        request = await self.friend_request_repo.get_request_by_id(request_id)
        if not request:
            raise NotFoundException("Friend request not found")

        # Verify user is the receiver
        if request.receiver_id != user_id:
            raise UnauthorizedException("Not authorized to reject this request")

        # Update request status
        request = await self.friend_request_repo.update_request_status(
            request_id, FriendRequestStatus.REJECTED
        )

        # Get sender info
        sender = await self.friend_repo.get_user_by_id(request.sender_id)

        return FriendRequestResponse(
            id=request.id,
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            status=request.status,
            created_at=request.created_at,
            responded_at=request.responded_at,
            sender_username=sender.username if sender else "Unknown",
            sender_profile_image=sender.profile_image if sender else None,
        )

    async def cancel_friend_request(
        self, request_id: str, user_id: str
    ) -> dict:
        """Cancel a sent friend request."""
        request = await self.friend_request_repo.get_request_by_id(request_id)
        if not request:
            raise NotFoundException("Friend request not found")

        # Verify user is the sender
        if request.sender_id != user_id:
            raise UnauthorizedException("Not authorized to cancel this request")

        # Delete request
        await self.friend_request_repo.delete_request(request_id)

        return {"message": "Friend request cancelled"}

    async def get_friends(self, user_id: str) -> FriendListResponse:
        """Get all friends of a user with presence information."""
        friendships = await self.friend_repo.get_user_friends(user_id)

        # Get presence for all friends if repository is available
        presence_map = {}
        if self.presence_repo:
            friend_ids = [f.friend_id for f in friendships]
            presences = await self.presence_repo.get_multiple_presence(friend_ids)
            presence_map = {p.id: p for p in presences}

        friends = []
        for friendship in friendships:
            friend_user = await self.friend_repo.get_user_by_id(friendship.friend_id)
            if friend_user:
                presence = presence_map.get(friendship.friend_id)
                friends.append(
                    FriendResponse(
                        id=friendship.id,
                        user_id=friendship.user_id,
                        friend_id=friendship.friend_id,
                        created_at=friendship.created_at,
                        is_blocked=friendship.is_blocked,
                        friend_username=friend_user.username,
                        friend_email=friend_user.email,
                        friend_profile_image=friend_user.profile_image,
                        friend_bio=friend_user.bio,
                        friend_is_online=presence.is_online if presence else False,
                        friend_last_seen_at=presence.last_seen_at if presence else None,
                        friend_status_message=presence.status_message if presence else None,
                    )
                )

        return FriendListResponse(friends=friends, total=len(friends))

    async def remove_friend(self, user_id: str, friend_id: str) -> dict:
        """Remove a friend."""
        # Check if friendship exists
        friendship = await self.friend_repo.get_friendship(user_id, friend_id)
        if not friendship:
            raise NotFoundException("Friendship not found")

        # Delete friendship
        await self.friend_repo.delete_friendship(user_id, friend_id)

        return {"message": "Friend removed"}

    async def block_friend(self, user_id: str, friend_id: str) -> dict:
        """Block a friend."""
        success = await self.friend_repo.block_friend(user_id, friend_id)
        if not success:
            raise NotFoundException("Friendship not found")

        return {"message": "Friend blocked"}

    async def unblock_friend(self, user_id: str, friend_id: str) -> dict:
        """Unblock a friend."""
        success = await self.friend_repo.unblock_friend(user_id, friend_id)
        if not success:
            raise NotFoundException("Friendship not found")

        return {"message": "Friend unblocked"}

    async def search_friends(self, user_id: str, params: FriendSearchParams) -> FriendListResponse:
        """Search and filter friends."""
        # Handle different filter types
        if params.filter_type == "online" and self.presence_repo:
            friendships = await self.friend_repo.get_online_friends(user_id)
        elif params.filter_type == "blocked":
            all_friends = await self.friend_repo.get_user_friends(user_id)
            friendships = [f for f in all_friends if f.is_blocked]
        elif params.query:
            friendships = await self.friend_repo.search_friends(user_id, params.query)
        else:
            friendships = await self.friend_repo.get_user_friends(user_id)

        # Limit results
        friendships = friendships[:params.limit]

        # Get presence for all friends
        presence_map = {}
        if self.presence_repo:
            friend_ids = [f.friend_id for f in friendships]
            presences = await self.presence_repo.get_multiple_presence(friend_ids)
            presence_map = {p.id: p for p in presences}

        friends = []
        for friendship in friendships:
            friend_user = await self.friend_repo.get_user_by_id(friendship.friend_id)
            if friend_user:
                presence = presence_map.get(friendship.friend_id)
                friends.append(
                    FriendResponse(
                        id=friendship.id,
                        user_id=friendship.user_id,
                        friend_id=friendship.friend_id,
                        created_at=friendship.created_at,
                        is_blocked=friendship.is_blocked,
                        friend_username=friend_user.username,
                        friend_email=friend_user.email,
                        friend_profile_image=friend_user.profile_image,
                        friend_bio=friend_user.bio,
                        friend_is_online=presence.is_online if presence else False,
                        friend_last_seen_at=presence.last_seen_at if presence else None,
                        friend_status_message=presence.status_message if presence else None,
                    )
                )

        return FriendListResponse(friends=friends, total=len(friends))

    async def create_friend_chat(self, user_id: str, friend_id: str):
        """Create or get direct chat with a friend.

        Note: This method returns the ChatRoomResponse from chat service.
        This is a placeholder that will be implemented when chat service is integrated.
        """
        # Verify friendship exists
        friendship = await self.friend_repo.get_friendship(user_id, friend_id)
        if not friendship:
            raise NotFoundException("Friendship not found")

        if friendship.is_blocked:
            raise ConflictException("Cannot create chat with blocked friend")

        # This will be implemented in the chat API endpoint
        # by calling chat service's create_direct_chat method
        return {"user_id": user_id, "friend_id": friend_id}
