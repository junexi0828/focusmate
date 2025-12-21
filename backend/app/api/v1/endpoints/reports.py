"""Report API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import DatabaseSession, get_current_user_required
from app.domain.report.schemas import ReportCreate, ReportResponse, ReportUpdate
from app.domain.report.service import ReportService
from app.infrastructure.repositories.report_repository import ReportRepository


router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_repository(db: DatabaseSession) -> ReportRepository:
    """Get report repository."""
    return ReportRepository(db)


def get_report_service(
    repo: Annotated[ReportRepository, Depends(get_report_repository)],
) -> ReportService:
    """Get report service."""
    return ReportService(repo)


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[ReportService, Depends(get_report_service)],
) -> ReportResponse:
    """Create a new report.

    Args:
        data: Report details
        current_user: Current authenticated user
        service: Report service

    Returns:
        Created report
    """
    try:
        return await service.create_report(current_user["id"], data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my", response_model=list[ReportResponse])
async def get_my_reports(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[ReportService, Depends(get_report_service)],
    limit: int = Query(50, ge=1, le=100),
) -> list[ReportResponse]:
    """Get all reports made by current user.

    Args:
        current_user: Current authenticated user
        service: Report service
        limit: Maximum number of reports to return

    Returns:
        List of user's reports
    """
    return await service.get_user_reports(current_user["id"], limit)


@router.get("/pending", response_model=list[ReportResponse])
async def get_pending_reports(
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[ReportService, Depends(get_report_service)],
    limit: int = Query(100, ge=1, le=200),
) -> list[ReportResponse]:
    """Get all pending reports (admin only).

    Args:
        current_user: Current authenticated user (must be admin)
        service: Report service
        limit: Maximum number of reports to return

    Returns:
        List of pending reports
    """
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view pending reports",
        )

    return await service.get_pending_reports(limit)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[ReportService, Depends(get_report_service)],
) -> ReportResponse:
    """Get report by ID.

    Args:
        report_id: Report identifier
        current_user: Current authenticated user
        service: Report service

    Returns:
        Report details

    Raises:
        HTTPException: If report not found or user not authorized
    """
    report = await service.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    # Users can only view their own reports, admins can view all
    if report.reporter_id != current_user["id"] and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own reports",
        )

    return report


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    data: ReportUpdate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[ReportService, Depends(get_report_service)],
) -> ReportResponse:
    """Update report status (admin only).

    Args:
        report_id: Report identifier
        data: Update data
        current_user: Current authenticated user (must be admin)
        service: Report service

    Returns:
        Updated report

    Raises:
        HTTPException: If user is not admin or report not found
    """
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update reports",
        )

    try:
        report = await service.update_report(report_id, current_user["id"], data)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
            )
        return report
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

