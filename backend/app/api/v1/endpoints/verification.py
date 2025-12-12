"""API endpoints for user verification."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile

from app.api.deps import DatabaseSession, get_current_user
from app.core.rbac import require_admin
from app.domain.verification.schemas import (
    VerificationResponse,
    VerificationReview,
    VerificationSettingsUpdate,
    VerificationStatusResponse,
    VerificationSubmit,
)
from app.domain.verification.service import VerificationService
from app.infrastructure.repositories.verification_repository import (
    VerificationRepository,
)

router = APIRouter(prefix="/verification", tags=["verification"])


def get_verification_service(
    db: Annotated[DatabaseSession, Depends()],
) -> VerificationService:
    """Get verification service dependency."""
    repository = VerificationRepository(db)
    return VerificationService(repository)


# User Endpoints
@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_verification(
    data: VerificationSubmit,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[VerificationService, Depends(get_verification_service)],
) -> dict:
    """Submit verification request."""
    try:
        verification = await service.submit_verification(current_user["id"], data)
        return {
            "verification_id": verification.verification_id,
            "status": verification.verification_status,
            "submitted_at": verification.submitted_at,
            "message": "인증 신청이 제출되었습니다. 관리자 검토 후 결과를 알려드립니다.",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/status")
async def get_verification_status(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[VerificationService, Depends(get_verification_service)],
) -> VerificationStatusResponse:
    """Get current user's verification status."""
    return await service.get_verification_status(current_user["id"])


@router.patch("/settings")
async def update_verification_settings(
    settings: VerificationSettingsUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[VerificationService, Depends(get_verification_service)],
) -> dict:
    """Update verification display settings."""
    try:
        verification = await service.update_settings(current_user["id"], settings)
        return {
            "badge_visible": verification.badge_visible,
            "department_visible": verification.department_visible,
            "message": "설정이 변경되었습니다.",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_verification_documents(
    files: list[UploadFile],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    """Upload verification documents."""
    from app.infrastructure.storage.file_upload import FileUploadService

    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 files allowed",
        )

    upload_service = FileUploadService(upload_dir="uploads/verification")

    try:
        file_paths = await upload_service.save_multiple_files(files, current_user["id"])
        file_urls = [upload_service.get_file_url(path) for path in file_paths]

        return {
            "uploaded_files": file_urls,
            "count": len(file_urls),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Admin Endpoints
@router.get("/admin/pending")
async def get_pending_verifications(
    current_user: Annotated[dict, Depends(require_admin)],
    service: Annotated[VerificationService, Depends(get_verification_service)],
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """Get pending verification requests (admin only)."""
    # if not current_user.get("is_admin"):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return await service.get_pending_verifications(page, per_page)


@router.post("/admin/{verification_id}/review")
async def review_verification(
    verification_id: UUID,
    review: VerificationReview,
    current_user: Annotated[dict, Depends(require_admin)],
    service: Annotated[VerificationService, Depends(get_verification_service)],
) -> dict:
    """Review verification request (admin only)."""
    # if not current_user.get("is_admin"):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        verification = await service.review_verification(
            verification_id, review.approved, review.admin_note
        )
        return {
            "verification_id": verification.verification_id,
            "status": verification.verification_status,
            "verified_at": verification.verified_at,
            "message": (
                "인증이 승인되었습니다."
                if review.approved
                else "인증이 반려되었습니다."
            ),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
