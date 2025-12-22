"""Service layer for user verification."""

import logging
from datetime import UTC, datetime
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


logger = logging.getLogger(__name__)


class VerificationService:
    """Service for user verification business logic."""

    def __init__(
        self,
        repository: VerificationRepository,
        user_repository: UserRepository | None = None,
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
            if existing.verification_status == "approved":
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

        # Send email notification to admin
        # If email is sent successfully, automatically approve verification
        email_sent_successfully = False
        email_error = None
        try:
            from app.core.config import settings
            from app.infrastructure.email.email_service import EmailService

            email_service = EmailService()

            # Get user info for admin email
            user_email = None
            username = "사용자"
            if self.user_repository:
                user = await self.user_repository.get_by_id(user_id)
                if user:
                    user_email = user.email
                    username = user.username or user.email.split("@")[0]

            # Send email to admin
            logger.info(
                f"[VERIFICATION] 📧 Email configuration check - SMTP_ENABLED={email_service.is_enabled}, ADMIN_EMAIL={settings.ADMIN_EMAIL}"
            )

            if settings.ADMIN_EMAIL and email_service.is_enabled:
                logger.info(
                    f"[VERIFICATION] ✅ Attempting to send verification email to admin: {settings.ADMIN_EMAIL}"
                )
                logger.info(
                    f"[VERIFICATION] User info: email={user_email}, username={username}, school={data.school_name}, department={data.department}, grade={data.grade}"
                )
                try:
                    # Convert grade to int if it's a string
                    grade_value = 0
                    if data.grade:
                        try:
                            grade_value = (
                                int(data.grade)
                                if isinstance(data.grade, str)
                                else data.grade
                            )
                        except (ValueError, TypeError):
                            grade_value = 0

                    logger.info(
                        f"[VERIFICATION] 📤 Calling send_verification_submitted_to_admin_email with: "
                        f"admin_email={settings.ADMIN_EMAIL}, user_email={user_email or f'user_{user_id}@example.com'}, "
                        f"username={username}, school_name={data.school_name}, department={data.department or '미지정'}, grade={grade_value}"
                    )

                    email_sent_successfully = (
                        await email_service.send_verification_submitted_to_admin_email(
                            admin_email=settings.ADMIN_EMAIL,
                            user_email=user_email or f"user_{user_id}@example.com",
                            username=username,
                            school_name=data.school_name,
                            department=data.department or "미지정",
                            grade=grade_value,
                        )
                    )

                    logger.info(
                        f"[VERIFICATION] 📬 Email send result: {email_sent_successfully} for verification {verification.verification_id}"
                    )

                    if email_sent_successfully:
                        logger.info(
                            f"[VERIFICATION] ✅ SMTP email sent successfully to admin. Auto-approving verification {verification.verification_id}"
                        )
                    else:
                        email_error = (
                            "SMTP 전송 실패 (인증은 정상적으로 제출되었습니다)"
                        )
                        logger.warning(
                            f"[VERIFICATION] ⚠️ SMTP email failed for verification {verification.verification_id}. "
                            f"Verification will remain pending. Check email service logs for details."
                        )
                except Exception as email_exc:
                    logger.error(
                        f"[VERIFICATION] ❌ Exception during SMTP send: {type(email_exc).__name__}: {email_exc}",
                        exc_info=True,
                    )
                    email_sent_successfully = False
                    email_error = f"SMTP 전송 중 예외 발생: {email_exc!s} (인증은 정상적으로 제출되었습니다)"
            else:
                logger.warning(
                    f"[VERIFICATION] ⚠️ SMTP not enabled or ADMIN_EMAIL not set. "
                    f"SMTP_ENABLED={email_service.is_enabled}, ADMIN_EMAIL={settings.ADMIN_EMAIL}"
                )
                email_error = (
                    "SMTP가 비활성화되어 있습니다 (인증은 정상적으로 제출되었습니다)"
                )
        except Exception as e:
            # Log error but don't fail verification submission
            logger.error(f"Failed to send admin notification email: {e}", exc_info=True)
            email_error = (
                f"이메일 전송 중 오류 발생: {e!s} (인증은 정상적으로 제출되었습니다)"
            )

        # If email was sent successfully, automatically approve verification
        if email_sent_successfully:
            try:
                verification = await self.repository.update_verification(
                    verification.verification_id,
                    {
                        "verification_status": "approved",
                        "verified_at": datetime.now(UTC),
                        "admin_note": "SMTP 전송 성공으로 자동 승인되었습니다.",
                    },
                )
                # Send approval email to user
                if self.user_repository:
                    user = await self.user_repository.get_by_id(user_id)
                    if user and user.email:
                        try:
                            from app.infrastructure.email.email_service import (
                                EmailService,
                            )

                            email_service = EmailService()
                            await email_service.send_verification_approved_email(
                                team_name=data.school_name,
                                leader_email=user.email,
                                admin_note="SMTP 전송 성공으로 자동 승인되었습니다.",
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to send approval email to user: {e}"
                            )
                if verification:
                    logger.info(
                        f"Verification {verification.verification_id} auto-approved after successful SMTP send"
                    )
            except Exception as e:
                logger.error(f"Failed to auto-approve verification: {e}")
        else:
            logger.warning(
                f"Verification {verification.verification_id} not auto-approved: SMTP send failed or disabled"
            )

        return VerificationResponse.model_validate(verification)

    async def get_verification_status(self, user_id: str) -> VerificationStatusResponse:
        """Get user's verification status."""
        verification = await self.repository.get_verification_by_user(user_id)

        if not verification:
            return VerificationStatusResponse(
                verification_id=None,
                status=None,
                school_name=None,
                department=None,
                major_category=None,
                grade=None,
                gender=None,
                badge_visible=None,
                department_visible=None,
                verified_at=None,
                message="인증 신청 내역이 없습니다.",
            )

        # Convert grade to string if it's not already
        grade_str = str(verification.grade) if verification.grade is not None else None

        return VerificationStatusResponse(
            verification_id=verification.verification_id,
            status=verification.verification_status,
            school_name=verification.school_name,
            department=verification.department,
            major_category=verification.major_category,
            grade=grade_str,
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
        self, verification_id: UUID, approved: bool, admin_note: str | None = None
    ) -> VerificationResponse:
        """Review verification request (admin)."""
        update_data = {
            "verification_status": "approved" if approved else "rejected",
            "admin_note": admin_note,
            "verified_at": datetime.now(UTC) if approved else None,
        }

        verification = await self.repository.update_verification(
            verification_id, update_data
        )

        if not verification:
            raise ValueError("Verification not found")

        # Send email notification
        from app.infrastructure.email.email_service import EmailService

        email_service = EmailService()

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
                    team_name=verification.school_name,  # Use school_name as team_name
                    leader_email=user_email,
                    admin_note=admin_note,
                )
        except Exception as e:
            # Log error but don't fail verification review
            logging.getLogger(__name__).error(f"Failed to send verification email: {e}")

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
        encryption_key = getattr(settings, "FILE_ENCRYPTION_KEY", None)

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

        encryption_key = getattr(settings, "FILE_ENCRYPTION_KEY", None)

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
