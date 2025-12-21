"""Report ORM Model for safety and moderation."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    """Report model for reporting inappropriate behavior in matching system.

    Attributes:
        report_id: Unique report identifier (UUID)
        reporter_id: User ID who made the report
        reported_user_id: User ID being reported (optional, for user reports)
        proposal_id: Matching proposal ID being reported (optional, for proposal reports)
        pool_id: Matching pool ID being reported (optional, for pool reports)
        report_type: Type of report (inappropriate_behavior, spam, harassment, other)
        reason: Detailed reason for the report
        status: Report status (pending, reviewed, resolved, dismissed)
        admin_note: Admin note/response (optional)
        reviewed_by: Admin user ID who reviewed (optional)
        reviewed_at: Timestamp when reviewed (optional)
    """

    __tablename__ = "reports"

    report_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="Unique report identifier",
    )

    reporter_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID who made the report",
    )

    reported_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User ID being reported",
    )

    proposal_id: Mapped[UUID | None] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("matching_proposals.proposal_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Matching proposal ID being reported",
    )

    pool_id: Mapped[UUID | None] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("matching_pools.pool_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Matching pool ID being reported",
    )

    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of report (inappropriate_behavior, spam, harassment, fake_profile, other)",
    )

    reason: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
        comment="Detailed reason for the report",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pending'"),
        index=True,
        comment="Report status (pending, reviewed, resolved, dismissed)",
    )

    admin_note: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True,
        comment="Admin note/response",
    )

    reviewed_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="Admin user ID who reviewed",
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(),
        nullable=True,
        comment="Timestamp when reviewed",
    )

    def __repr__(self) -> str:
        return f"<Report(report_id={self.report_id}, report_type={self.report_type}, status={self.status})>"

