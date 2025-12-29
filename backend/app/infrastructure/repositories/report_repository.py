"""Report repository for database operations."""

from uuid import UUID
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.report import Report


class ReportRepository:
    """Repository for report database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create(self, report_data: dict) -> Report:
        """Create a new report."""
        report = Report(**report_data)
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_by_id(self, report_id: UUID) -> Optional[Report]:
        """Get report by ID."""
        result = await self.session.execute(
            select(Report).where(Report.report_id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_by_reporter(self, reporter_id: str, limit: int = 50) -> List[Report]:
        """Get all reports made by a user."""
        result = await self.session.execute(
            select(Report)
            .where(Report.reporter_id == reporter_id)
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_reports(self, limit: int = 100) -> List[Report]:
        """Get all pending reports (admin only)."""
        result = await self.session.execute(
            select(Report)
            .where(Report.status == "pending")
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_proposal(self, proposal_id: UUID) -> List[Report]:
        """Get all reports for a specific proposal."""
        result = await self.session.execute(
            select(Report)
            .where(Report.proposal_id == proposal_id)
            .order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_pool(self, pool_id: UUID) -> List[Report]:
        """Get all reports for a specific pool."""
        result = await self.session.execute(
            select(Report)
            .where(Report.pool_id == pool_id)
            .order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, report_id: UUID, update_data: dict) -> Optional[Report]:
        """Update report."""
        report = await self.get_by_id(report_id)
        if not report:
            return None

        for key, value in update_data.items():
            if value is not None:
                setattr(report, key, value)

        await self.session.commit()
        await self.session.refresh(report)
        return report

