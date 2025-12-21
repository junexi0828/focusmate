"""Report domain service."""

from datetime import UTC
from uuid import UUID

from app.domain.report.schemas import ReportCreate, ReportResponse, ReportUpdate
from app.infrastructure.repositories.report_repository import ReportRepository


class ReportService:
    """Service for report business logic."""

    def __init__(self, repository: ReportRepository):
        """Initialize service with repository."""
        self.repository = repository

    async def create_report(self, reporter_id: str, data: ReportCreate) -> ReportResponse:
        """Create a new report.

        Args:
            reporter_id: User ID making the report
            data: Report details

        Returns:
            Created report

        Raises:
            ValueError: If report data is invalid
        """
        # Validate that at least one target is specified
        if not data.reported_user_id and not data.proposal_id and not data.pool_id:
            raise ValueError("At least one target (user, proposal, or pool) must be specified")

        # Validate report type
        valid_types = ["inappropriate_behavior", "spam", "harassment", "fake_profile", "other"]
        if data.report_type not in valid_types:
            raise ValueError(f"Invalid report type. Must be one of: {valid_types}")

        report_data = {
            "reporter_id": reporter_id,
            "reported_user_id": data.reported_user_id,
            "proposal_id": data.proposal_id,
            "pool_id": data.pool_id,
            "report_type": data.report_type,
            "reason": data.reason,
            "status": "pending",
        }

        report = await self.repository.create(report_data)
        return ReportResponse.model_validate(report)

    async def get_report(self, report_id: UUID) -> ReportResponse | None:
        """Get report by ID."""
        report = await self.repository.get_by_id(report_id)
        if not report:
            return None
        return ReportResponse.model_validate(report)

    async def get_user_reports(self, reporter_id: str, limit: int = 50) -> list[ReportResponse]:
        """Get all reports made by a user."""
        reports = await self.repository.get_by_reporter(reporter_id, limit)
        return [ReportResponse.model_validate(r) for r in reports]

    async def get_pending_reports(self, limit: int = 100) -> list[ReportResponse]:
        """Get all pending reports (admin only)."""
        reports = await self.repository.get_pending_reports(limit)
        return [ReportResponse.model_validate(r) for r in reports]

    async def update_report(
        self, report_id: UUID, reviewer_id: str, data: ReportUpdate
    ) -> ReportResponse | None:
        """Update report status (admin only).

        Args:
            report_id: Report identifier
            reviewer_id: Admin user ID reviewing the report
            data: Update data

        Returns:
            Updated report or None if not found
        """
        from datetime import datetime

        update_data = {}
        if data.status:
            valid_statuses = ["pending", "reviewed", "resolved", "dismissed"]
            if data.status not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
            update_data["status"] = data.status
            update_data["reviewed_by"] = reviewer_id
            update_data["reviewed_at"] = datetime.now(UTC)

        if data.admin_note is not None:
            update_data["admin_note"] = data.admin_note

        if not update_data:
            return await self.get_report(report_id)

        report = await self.repository.update(report_id, update_data)
        if not report:
            return None
        return ReportResponse.model_validate(report)

