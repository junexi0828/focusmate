"""Service layer for user verification."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.verification.schemas import (
    VerificationResponse,
    VerificationSettingsUpdate,
    VerificationStatusResponse,
    VerificationSubmit,
)
from app.infrastructure.repositories.verification_repository import (
    VerificationRepository,
)


class VerificationService:
    """Service for user verification business logic."""

    def __init__(self, repository: VerificationRepository):
        self.repository = repository

    async def submit_verification(
        self, user_id: str, data: VerificationSubmit
    ) -> VerificationResponse:
        """Submit a verification request."""
        # Check if user already has verification
        existing = await self.repository.get_verification_by_user(user_id)
        if existing:
            if existing.verification_status == "pending":
                raise ValueError("Verification request already submitted and pending")
            elif existing.verification_status == "approved":
                raise ValueError("User is already verified")

        # Encrypt student ID if provided
        student_id_encrypted = None
        if data.student_id:
            # TODO: Implement encryption
            student_id_encrypted = data.student_id  # Placeholder

        # Create verification request
        verification_data = {
            "user_id": user_id,
            "school_name": data.school_name,
            "department": data.department,
            "major_category": data.major_category,
            "grade": data.grade,
            "student_id_encrypted": student_id_encrypted,
            "gender": data.gender,
            "submitted_documents": data.documents,
            "verification_status": "pending",
        }

        verification = await self.repository.create_verification(verification_data)
        return VerificationResponse.model_validate(verification)

    async def get_verification_status(
        self, user_id: str
    ) -> VerificationStatusResponse:
        """Get user's verification status."""
        verification = await self.repository.get_verification_by_user(user_id)

        if not verification:
            return VerificationStatusResponse(
                verification_id=None,
                status=None,
                message="No verification request found",
            )

        return VerificationStatusResponse(
            verification_id=verification.verification_id,
            status=verification.verification_status,
            school_name=verification.school_name,
            department=verification.department,
            major_category=verification.major_category,
            grade=verification.grade,
            gender=verification.gender,
            badge_visible=verification.badge_visible,
            department_visible=verification.department_visible,
            verified_at=verification.verified_at,
            message=self._get_status_message(verification.verification_status),
        )

    async def update_settings(
        self, user_id: str, settings: VerificationSettingsUpdate
    ) -> VerificationResponse:
        """Update verification display settings."""
        settings_dict = settings.model_dump(exclude_unset=True)

        verification = await self.repository.update_verification_settings(
            user_id, settings_dict
        )

        if not verification:
            raise ValueError("Verification not found")

        return VerificationResponse.model_validate(verification)

    async def get_pending_verifications(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """Get pending verification requests (admin)."""
        offset = (page - 1) * per_page
        verifications = await self.repository.get_pending_verifications(
            limit=per_page, offset=offset
        )
        total = await self.repository.count_pending_verifications()

        return {
            "verifications": [
                {
                    "verification_id": v.verification_id,
                    "user_id": v.user_id,
                    "school_name": v.school_name,
                    "department": v.department,
                    "grade": v.grade,
                    "gender": v.gender,
                    "documents": v.submitted_documents or [],
                    "submitted_at": v.submitted_at,
                }
                for v in verifications
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    async def review_verification(
        self, verification_id: UUID, approved: bool, admin_note: Optional[str] = None
    ) -> VerificationResponse:
        """Review verification request (admin)."""
        update_data = {
            "verification_status": "approved" if approved else "rejected",
            "admin_note": admin_note,
            "verified_at": datetime.utcnow() if approved else None,
        }

        verification = await self.repository.update_verification(
            verification_id, update_data
        )

        if not verification:
            raise ValueError("Verification not found")

        # TODO: Send email notification

        return VerificationResponse.model_validate(verification)

    def _get_status_message(self, status: str) -> str:
        """Get status message."""
        messages = {
            "pending": "Verification request is pending admin review",
            "approved": "Verification approved",
            "rejected": "Verification rejected. Please submit again with correct documents",
        }
        return messages.get(status, "Unknown status")
