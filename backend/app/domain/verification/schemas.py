"""Pydantic schemas for user verification."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class VerificationSubmit(BaseModel):
    """Schema for submitting verification request."""

    school_name: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=1, max_length=100)
    major_category: Optional[str] = Field(None, max_length=50)
    grade: str = Field(..., min_length=1, max_length=20)
    student_id: Optional[str] = Field(None, max_length=20)
    gender: str = Field(..., pattern="^(male|female|other)$")
    documents: list[str] = Field(default_factory=list)

    @field_validator("documents")
    @classmethod
    def validate_documents(cls, v: list[str]) -> list[str]:
        if len(v) > 5:
            raise ValueError("Maximum 5 documents allowed")
        return v


class VerificationResponse(BaseModel):
    """Schema for verification response."""

    verification_id: UUID
    user_id: str
    school_name: str
    department: str
    major_category: Optional[str]
    grade: str
    gender: str
    verification_status: str
    badge_visible: bool
    department_visible: bool
    submitted_at: datetime
    verified_at: Optional[datetime]

    class Config:
        from_attributes = True


class VerificationStatusResponse(BaseModel):
    """Schema for verification status response."""

    verification_id: Optional[UUID]
    status: Optional[str]
    school_name: Optional[str]
    department: Optional[str]
    major_category: Optional[str]
    grade: Optional[str]
    gender: Optional[str]
    badge_visible: Optional[bool]
    department_visible: Optional[bool]
    verified_at: Optional[datetime]
    message: Optional[str]


class VerificationSettingsUpdate(BaseModel):
    """Schema for updating verification settings."""

    badge_visible: Optional[bool] = None
    department_visible: Optional[bool] = None


class VerificationReview(BaseModel):
    """Schema for admin verification review."""

    approved: bool
    admin_note: Optional[str] = Field(None, max_length=500)


class VerificationListItem(BaseModel):
    """Schema for verification list item (admin)."""

    verification_id: UUID
    user_id: str
    user_name: str
    school_name: str
    department: str
    grade: str
    gender: str
    documents: list[str]
    submitted_at: datetime

    class Config:
        from_attributes = True
