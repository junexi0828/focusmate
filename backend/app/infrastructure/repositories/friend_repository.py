"""Friend repository."""

from datetime import UTC, datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.friend import Friend, FriendRequest, FriendRequestStatus
from app.infrastructure.database.models.user import User


class FriendRequestRepository:
    """Repository for friend request operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_request(self, sender_id: str, receiver_id: str, request_id: str) -> FriendRequest:
        """Create a new friend request."""
        request = FriendRequest(
            id=request_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            status=FriendRequestStatus.PENDING,
        )
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_request_by_id(self, request_id: str) -> FriendRequest | None:
        """Get friend request by ID."""
        result = await self.session.execute(
            select(FriendRequest).where(FriendRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_request(self, sender_id: str, receiver_id: str) -> FriendRequest | None:
        """Get pending friend request between two users."""
        result = await self.session.execute(
            select(FriendRequest).where(
                and_(
                    FriendRequest.sender_id == sender_id,
                    FriendRequest.receiver_id == receiver_id,
                    FriendRequest.status == FriendRequestStatus.PENDING,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_sent_requests(self, user_id: str) -> list[FriendRequest]:
        """Get all friend requests sent by user."""
        result = await self.session.execute(
            select(FriendRequest)
            .where(FriendRequest.sender_id == user_id)
            .order_by(FriendRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_received_requests(
        self, user_id: str, pending_only: bool = False
    ) -> list[FriendRequest]:
        """Get all friend requests received by user."""
        query = select(FriendRequest).where(FriendRequest.receiver_id == user_id)

        if pending_only:
            query = query.where(FriendRequest.status == FriendRequestStatus.PENDING)

        query = query.order_by(FriendRequest.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_request_status(
        self, request_id: str, status: FriendRequestStatus
    ) -> FriendRequest | None:
        """Update friend request status."""
        request = await self.get_request_by_id(request_id)
        if request:
            request.status = status
            request.responded_at = datetime.now(UTC)
            await self.session.commit()
            await self.session.refresh(request)
        return request

    async def delete_request(self, request_id: str) -> bool:
        """Delete a friend request."""
        request = await self.get_request_by_id(request_id)
        if request:
            await self.session.delete(request)
            await self.session.commit()
            return True
        return False


class FriendRepository:
    """Repository for friend operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_friendship(
        self, user_id: str, friend_id: str, friendship_id_1: str, friendship_id_2: str
    ) -> tuple[Friend, Friend]:
        """Create bidirectional friendship."""
        friendship1 = Friend(
            id=friendship_id_1,
            user_id=user_id,
            friend_id=friend_id,
        )
        friendship2 = Friend(
            id=friendship_id_2,
            user_id=friend_id,
            friend_id=user_id,
        )
        self.session.add(friendship1)
        self.session.add(friendship2)
        await self.session.commit()
        await self.session.refresh(friendship1)
        await self.session.refresh(friendship2)
        return friendship1, friendship2

    async def get_friendship(self, user_id: str, friend_id: str) -> Friend | None:
        """Get friendship between two users."""
        result = await self.session.execute(
            select(Friend).where(
                and_(
                    Friend.user_id == user_id,
                    Friend.friend_id == friend_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_friends(self, user_id: str) -> list[Friend]:
        """Get all friends of a user."""
        result = await self.session.execute(
            select(Friend)
            .where(Friend.user_id == user_id)
            .order_by(Friend.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_friendship(self, user_id: str, friend_id: str) -> bool:
        """Delete bidirectional friendship."""
        # Delete both directions
        result1 = await self.session.execute(
            select(Friend).where(
                and_(
                    Friend.user_id == user_id,
                    Friend.friend_id == friend_id,
                )
            )
        )
        friendship1 = result1.scalar_one_or_none()

        result2 = await self.session.execute(
            select(Friend).where(
                and_(
                    Friend.user_id == friend_id,
                    Friend.friend_id == user_id,
                )
            )
        )
        friendship2 = result2.scalar_one_or_none()

        deleted = False
        if friendship1:
            await self.session.delete(friendship1)
            deleted = True
        if friendship2:
            await self.session.delete(friendship2)
            deleted = True

        if deleted:
            await self.session.commit()
        return deleted

    async def block_friend(self, user_id: str, friend_id: str) -> bool:
        """Block a friend."""
        friendship = await self.get_friendship(user_id, friend_id)
        if friendship:
            friendship.is_blocked = True
            await self.session.commit()
            return True
        return False

    async def unblock_friend(self, user_id: str, friend_id: str) -> bool:
        """Unblock a friend."""
        friendship = await self.get_friendship(user_id, friend_id)
        if friendship:
            friendship.is_blocked = False
            await self.session.commit()
            return True
        return False

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def search_friends(self, user_id: str, query: str) -> list[Friend]:
        """Search friends by username."""
        from app.infrastructure.database.models.user import User

        result = await self.session.execute(
            select(Friend)
            .join(User, Friend.friend_id == User.id)
            .where(
                and_(
                    Friend.user_id == user_id,
                    User.username.ilike(f"%{query}%"),
                )
            )
            .order_by(Friend.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_online_friends(self, user_id: str) -> list[Friend]:
        """Get friends who are currently online."""
        from app.infrastructure.database.models.presence import UserPresence

        result = await self.session.execute(
            select(Friend)
            .join(UserPresence, Friend.friend_id == UserPresence.id)
            .where(
                and_(
                    Friend.user_id == user_id,
                    UserPresence.is_online == True,
                )
            )
            .order_by(Friend.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_friends_with_presence(self, user_id: str) -> list[tuple[Friend, User, object]]:
        """Get friends with their user info and presence.

        Returns list of tuples: (Friend, User, UserPresence or None)
        """

        from app.infrastructure.database.models.presence import UserPresence
        from app.infrastructure.database.models.user import User

        result = await self.session.execute(
            select(Friend, User, UserPresence)
            .join(User, Friend.friend_id == User.id)
            .outerjoin(UserPresence, Friend.friend_id == UserPresence.id)
            .where(Friend.user_id == user_id)
            .order_by(Friend.created_at.desc())
        )
        return list(result.all())
