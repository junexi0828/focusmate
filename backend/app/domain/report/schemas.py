"""Report domain schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Schema for creating a new report."""

    reported_user_id: str | None = Field(None, description="User ID being reported")
    proposal_id: UUID | None = Field(None, description="Matching proposal ID being reported")
    pool_id: UUID | None = Field(None, description="Matching pool ID being reported")
    report_type: str = Field(
        ...,
        description="Type of report (inappropriate_behavior, spam, harassment, fake_profile, other)",
    )
    reason: str = Field(..., min_length=10, max_length=1000, description="Detailed reason for the report")


class ReportResponse(BaseModel):
    """Schema for report response."""

    report_id: UUID
    reporter_id: str
    reported_user_id: str | None = None
    proposal_id: UUID | None = None
    pool_id: UUID | None = None
    report_type: str
    reason: str
    status: str
    admin_note: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportUpdate(BaseModel):
    """Schema for updating a report (admin only)."""

    status: str | None = Field(None, description="Report status (pending, reviewed, resolved, dismissed)")
    admin_note: str | None = Field(None, max_length=1000, description="Admin note/response")

