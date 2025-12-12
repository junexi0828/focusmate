"""Repository for matching pool operations."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.matching import MatchingPool


class MatchingPoolRepository:
    """Repository for matching pool database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_pool(self, pool_data: dict) -> MatchingPool:
        """Create a new matching pool."""
        pool = MatchingPool(**pool_data)
        self.session.add(pool)
        await self.session.commit()
        await self.session.refresh(pool)
        return pool

    async def get_pool_by_id(self, pool_id: UUID) -> Optional[MatchingPool]:
        """Get pool by ID."""
        result = await self.session.execute(
            select(MatchingPool).where(MatchingPool.pool_id == pool_id)
        )
        return result.scalar_one_or_none()

    async def get_pool_by_creator(self, creator_id: str) -> Optional[MatchingPool]:
        """Get active pool by creator ID."""
        result = await self.session.execute(
            select(MatchingPool)
            .where(MatchingPool.creator_id == creator_id)
            .where(MatchingPool.status == "waiting")
        )
        return result.scalar_one_or_none()

    async def get_user_active_pool(self, user_id: str) -> Optional[MatchingPool]:
        """Get active pool where user is a member."""
        result = await self.session.execute(
            select(MatchingPool)
            .where(MatchingPool.member_ids.contains([user_id]))
            .where(MatchingPool.status == "waiting")
        )
        return result.scalar_one_or_none()

    async def get_waiting_pools(
        self, exclude_pool_id: Optional[UUID] = None
    ) -> list[MatchingPool]:
        """Get all waiting pools."""
        query = select(MatchingPool).where(MatchingPool.status == "waiting")

        if exclude_pool_id:
            query = query.where(MatchingPool.pool_id != exclude_pool_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_matching_candidates(
        self,
        member_count: int,
        gender: str,
        exclude_pool_id: UUID,
    ) -> list[MatchingPool]:
        """Get matching candidates with same member count and different gender."""
        opposite_gender = "female" if gender == "male" else "male"

        result = await self.session.execute(
            select(MatchingPool)
            .where(MatchingPool.status == "waiting")
            .where(MatchingPool.member_count == member_count)
            .where(MatchingPool.gender == opposite_gender)
            .where(MatchingPool.pool_id != exclude_pool_id)
            .where(MatchingPool.expires_at > datetime.utcnow())
        )
        return list(result.scalars().all())

    async def update_pool(
        self, pool_id: UUID, update_data: dict
    ) -> Optional[MatchingPool]:
        """Update pool."""
        pool = await self.get_pool_by_id(pool_id)
        if not pool:
            return None

        for key, value in update_data.items():
            setattr(pool, key, value)

        await self.session.commit()
        await self.session.refresh(pool)
        return pool

    async def delete_pool(self, pool_id: UUID) -> bool:
        """Delete pool."""
        pool = await self.get_pool_by_id(pool_id)
        if not pool:
            return False

        await self.session.delete(pool)
        await self.session.commit()
        return True

    async def get_pool_statistics(self) -> dict:
        """Get pool statistics."""
        # Total waiting pools
        total_result = await self.session.execute(
            select(func.count(MatchingPool.pool_id)).where(
                MatchingPool.status == "waiting"
            )
        )
        total_waiting = total_result.scalar() or 0

        # By member count
        member_count_result = await self.session.execute(
            select(
                MatchingPool.member_count, func.count(MatchingPool.pool_id)
            ).where(MatchingPool.status == "waiting").group_by(MatchingPool.member_count)
        )
        by_member_count = {
            str(row[0]): row[1] for row in member_count_result.all()
        }

        # By gender
        gender_result = await self.session.execute(
            select(MatchingPool.gender, func.count(MatchingPool.pool_id))
            .where(MatchingPool.status == "waiting")
            .group_by(MatchingPool.gender)
        )
        by_gender = {row[0]: row[1] for row in gender_result.all()}

        # Average wait time
        avg_wait_result = await self.session.execute(
            select(func.avg(func.extract("epoch", datetime.utcnow() - MatchingPool.created_at) / 3600))
            .where(MatchingPool.status == "waiting")
        )
        average_wait_time_hours = avg_wait_result.scalar() or 0.0

        return {
            "total_waiting": total_waiting,
            "by_member_count": by_member_count,
            "by_gender": by_gender,
            "average_wait_time_hours": round(average_wait_time_hours, 2),
        }

    async def expire_old_pools(self) -> int:
        """Expire pools that are past expiration date."""
        result = await self.session.execute(
            select(MatchingPool)
            .where(MatchingPool.status == "waiting")
            .where(MatchingPool.expires_at < datetime.utcnow())
        )
        expired_pools = result.scalars().all()

        for pool in expired_pools:
            pool.status = "expired"

        await self.session.commit()
        return len(expired_pools)
