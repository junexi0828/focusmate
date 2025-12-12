"""User verification database models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ARRAY, Boolean, ForeignKey, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class UserVerification(Base):
    """User verification model for school/department authentication."""

    __tablename__ = "user_verification"

    verification_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # School information
    school_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Department information
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    major_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Grade information
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    student_id_encrypted: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    # Personal information
    gender: Mapped[str] = mapped_column(String(10), nullable=False)

    # Verification information
    verification_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pending"
    )
    submitted_documents: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text()), nullable=True
    )
    admin_note: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    # Display settings
    badge_visible: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default="true"
    )
    department_visible: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default="true"
    )

    # Timestamps
    submitted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default="CURRENT_TIMESTAMP"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="verification")

    def __repr__(self) -> str:
        return f"<UserVerification(user_id={self.user_id}, status={self.verification_status})>"
