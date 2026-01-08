"""RefreshToken Repository."""

from datetime import datetime, UTC
from uuid import uuid4
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Repository for refresh token operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(
        self,
        user_id: str,
        family_id: str,
        expires_at: datetime,
        absolute_expires_at: datetime,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> RefreshToken:
        """Create a new refresh token.

        Args:
            user_id: User identifier
            family_id: Token family identifier
            expires_at: Rolling expiry timestamp
            absolute_expires_at: Absolute expiry timestamp
            device_info: Device/browser information
            ip_address: IP address

        Returns:
            Created refresh token
        """
        token_id = str(uuid4())

        refresh_token = RefreshToken(
            id=str(uuid4()),
            user_id=user_id,
            token_id=token_id,
            family_id=family_id,
            expires_at=expires_at,
            absolute_expires_at=absolute_expires_at,
            last_rotated_at=datetime.now(UTC),
            device_info=device_info,
            ip_address=ip_address,
            created_at=datetime.now(UTC),
        )

        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)

        return refresh_token

    async def get_by_token_id(self, token_id: str) -> RefreshToken | None:
        """Get refresh token by token_id.

        Args:
            token_id: JWT jti claim

        Returns:
            Refresh token if found, None otherwise
        """
        stmt = select(RefreshToken).where(RefreshToken.token_id == token_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, token: RefreshToken) -> RefreshToken:
        """Update refresh token.

        Args:
            token: Token to update

        Returns:
            Updated token
        """
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def revoke_family(self, family_id: str) -> None:
        """Revoke all tokens in a family (for theft detection).

        Args:
            family_id: Token family identifier
        """
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id)
            .values(expires_at=datetime.now(UTC))
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_expired(self) -> int:
        """Delete expired tokens (cleanup job).

        Returns:
            Number of deleted tokens
        """
        stmt = delete(RefreshToken).where(
            RefreshToken.absolute_expires_at < datetime.now(UTC)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount or 0
