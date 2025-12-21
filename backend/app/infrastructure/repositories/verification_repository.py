"""Repository for user verification operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.verification import UserVerification


class VerificationRepository:
    """Repository for user verification database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_verification(self, verification_data: dict) -> UserVerification:
        """Create a new verification request."""
        verification = UserVerification(**verification_data)
        self.session.add(verification)
        await self.session.commit()
        await self.session.refresh(verification)
        return verification

    async def get_verification_by_id(
        self, verification_id: UUID
    ) -> UserVerification | None:
        """Get verification by ID."""
        result = await self.session.execute(
            select(UserVerification).where(
                UserVerification.verification_id == verification_id
            )
        )
        return result.scalar_one_or_none()

    async def get_verification_by_user(
        self, user_id: str
    ) -> UserVerification | None:
        """Get verification by user ID."""
        result = await self.session.execute(
            select(UserVerification).where(UserVerification.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_verifications(
        self, limit: int = 100, offset: int = 0
    ) -> list[UserVerification]:
        """Get pending verification requests."""
        result = await self.session.execute(
            select(UserVerification)
            .where(UserVerification.verification_status == "pending")
            .order_by(UserVerification.submitted_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update_verification(
        self, verification_id: UUID, update_data: dict
    ) -> UserVerification | None:
        """Update verification."""
        verification = await self.get_verification_by_id(verification_id)
        if not verification:
            return None

        for key, value in update_data.items():
            setattr(verification, key, value)

        await self.session.commit()
        await self.session.refresh(verification)
        return verification

    async def update_verification_settings(
        self, user_id: str, settings: dict
    ) -> UserVerification | None:
        """Update verification display settings."""
        verification = await self.get_verification_by_user(user_id)
        if not verification:
            return None

        for key, value in settings.items():
            if hasattr(verification, key):
                setattr(verification, key, value)

        await self.session.commit()
        await self.session.refresh(verification)
        return verification

    async def count_pending_verifications(self) -> int:
        """Count pending verification requests."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(UserVerification.verification_id)).where(
                UserVerification.verification_status == "pending"
            )
        )
        return result.scalar() or 0
