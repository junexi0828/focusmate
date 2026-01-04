"""User repository implementation."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.user import User


class UserRepository:
    """Repository for user data access."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, user: User) -> User:
        """Create user."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_ids(self, user_ids: list[str]) -> list[User]:
        """Get multiple users by IDs in a single query.

        This method prevents N+1 query problems by fetching all users at once.
        Industry standard pattern (DataLoader-inspired).

        Args:
            user_ids: List of user IDs to fetch

        Returns:
            List of User objects (may be fewer than requested if some don't exist)
        """
        if not user_ids:
            return []

        result = await self.db.execute(
            select(User).where(User.id.in_(user_ids))
        )
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        """Update user."""
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Delete user."""
        await self.db.delete(user)
        await self.db.flush()

    async def get_by_password_reset_token(self, token: str) -> User | None:
        """Get user by password reset token."""
        result = await self.db.execute(
            select(User).where(User.password_reset_token == token)
        )
        return result.scalar_one_or_none()

    async def get_by_naver_id(self, naver_id: str) -> User | None:
        """Get user by Naver OAuth ID."""
        result = await self.db.execute(
            select(User).where(User.naver_id == naver_id)
        )
        return result.scalar_one_or_none()
