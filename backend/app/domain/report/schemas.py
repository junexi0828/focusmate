"""Report domain schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Schema for creating a new report."""

    reported_user_id: Optional[str] = Field(None, description="User ID being reported")
    proposal_id: Optional[UUID] = Field(None, description="Matching proposal ID being reported")
    pool_id: Optional[UUID] = Field(None, description="Matching pool ID being reported")
    report_type: str = Field(
        ...,
        description="Type of report (inappropriate_behavior, spam, harassment, fake_profile, other)",
    )
    reason: str = Field(..., min_length=10, max_length=1000, description="Detailed reason for the report")


class ReportResponse(BaseModel):
    """Schema for report response."""

    report_id: UUID
    reporter_id: str
    reported_user_id: Optional[str] = None
    proposal_id: Optional[UUID] = None
    pool_id: Optional[UUID] = None
    report_type: str
    reason: str
    status: str
    admin_note: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportUpdate(BaseModel):
    """Schema for updating a report (admin only)."""

    status: Optional[str] = Field(None, description="Report status (pending, reviewed, resolved, dismissed)")
    admin_note: Optional[str] = Field(None, max_length=1000, description="Admin note/response")

