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
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.verification_repository import (
    VerificationRepository,
)


class VerificationService:
    """Service for user verification business logic."""

    def __init__(
        self, repository: VerificationRepository, user_repository: UserRepository | None = None
    ):
        self.repository = repository
        self.user_repository = user_repository

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
            from app.shared.utils.encryption import get_encryption_service

            encryption_service = get_encryption_service()
            student_id_encrypted = encryption_service.encrypt_string(data.student_id)

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

        # Send email notification
        from app.infrastructure.email.email_service import EmailService
        from app.core.config import settings

        email_service = EmailService(
            smtp_host=settings.SMTP_HOST,
            smtp_port=settings.SMTP_PORT,
            from_name=settings.SMTP_FROM_NAME,
            from_email=settings.SMTP_FROM_EMAIL,
            smtp_user=settings.SMTP_USER if settings.SMTP_ENABLED else None,
            smtp_password=settings.SMTP_PASSWORD if settings.SMTP_ENABLED else None,
        )

        # Get user email from user repository
        user_email = None
        if self.user_repository:
            user = await self.user_repository.get_by_id(verification.user_id)
            if user:
                user_email = user.email

        # Fallback if user not found or repository not available
        if not user_email:
            user_email = f"user_{verification.user_id}@example.com"

        # Note: Email sending is optional and can be disabled if SMTP is not configured
        try:
            if approved:
                await email_service.send_verification_approved_email(
                    team_name=verification.school_name,  # Use school_name as team_name
                    leader_email=user_email,
                    admin_note=admin_note or "",
                )
            else:
                await email_service.send_verification_rejected_email(
                    user_email=user_email,
                    team_name=verification.school_name,  # Use school_name as team_name
                    admin_note=admin_note,
                )
        except Exception as e:
            # Log error but don't fail verification review
            print(f"Failed to send verification email: {e}")

        return VerificationResponse.model_validate(verification)

    async def _encrypt_file(self, content: bytes) -> bytes:
        """Encrypt file content using Fernet symmetric encryption.

        Args:
            content: Raw file content

        Returns:
            Encrypted content
        """
        from cryptography.fernet import Fernet
        from app.core.config import settings

        # Use encryption key from settings or generate one
        # In production, this should be stored securely (e.g., environment variable)
        encryption_key = getattr(settings, 'FILE_ENCRYPTION_KEY', None)

        if not encryption_key:
            # Generate a key for development (NOT for production!)
            # In production, use a fixed key from environment
            encryption_key = Fernet.generate_key()

        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()

        cipher = Fernet(encryption_key)
        return cipher.encrypt(content)

    async def _decrypt_file(self, encrypted_content: bytes) -> bytes:
        """Decrypt file content.

        Args:
            encrypted_content: Encrypted file content

        Returns:
            Decrypted content
        """
        from cryptography.fernet import Fernet
        from app.core.config import settings

        encryption_key = getattr(settings, 'FILE_ENCRYPTION_KEY', None)

        if not encryption_key:
            raise ValueError("Encryption key not configured")

        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()

        cipher = Fernet(encryption_key)
        return cipher.decrypt(encrypted_content)

    def _get_status_message(self, status: str) -> str:
        """Get status message."""
        messages = {
            "pending": "Verification request is pending admin review",
            "approved": "Verification approved",
            "rejected": "Verification rejected. Please submit again with correct documents",
        }
        return messages.get(status, "Unknown status")
