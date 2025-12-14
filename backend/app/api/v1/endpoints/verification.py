"""API endpoints for user verification."""

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import Response

from app.api.deps import DatabaseSession, get_current_user
from app.core.rbac import require_admin
from app.domain.verification.schemas import (
    VerificationReview,
    VerificationSettingsUpdate,
    VerificationStatusResponse,
    VerificationSubmit,
)
from app.domain.verification.service import VerificationService
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.verification_repository import (
    VerificationRepository,
)

router = APIRouter(prefix="/verification", tags=["verification"])


def get_verification_service(
    db: DatabaseSession,
) -> VerificationService:
    """Get verification service dependency."""
    repository = VerificationRepository(db)
    user_repository = UserRepository(db)
    return VerificationService(repository, user_repository)


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
    """Upload verification documents (encrypted)."""
    from app.infrastructure.storage.encrypted_file_upload import EncryptedFileUploadService

    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 files allowed",
        )

    # Use encrypted file upload service
    upload_service = EncryptedFileUploadService(
        upload_dir="uploads/verification", encrypt=True
    )

    try:
        file_paths = await upload_service.save_multiple_files(files, current_user["id"])
        file_urls = [upload_service.get_file_url(path) for path in file_paths]

        return {
            "uploaded_files": file_urls,
            "count": len(file_urls),
            "encrypted": True,
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


@router.get("/admin/file/{file_path:path}")
async def download_verification_file(
    file_path: str,
    current_user: Annotated[dict, Depends(require_admin)],
) -> Response:
    """Download verification file (admin only, automatically decrypted).

    Args:
        file_path: Relative file path (e.g., verification/user_id/filename.encrypted)
        current_user: Current authenticated admin user

    Returns:
        File content with appropriate headers
    """
    from app.infrastructure.storage.encrypted_file_upload import EncryptedFileUploadService

    upload_service = EncryptedFileUploadService(
        upload_dir="uploads/verification", encrypt=False
    )

    try:
        # Read and decrypt file
        content = await upload_service.read_file(file_path, decrypt=True)

        # Determine content type from file extension
        path = Path(file_path)
        content_type = "application/octet-stream"
        if path.suffix.lower() in [".jpg", ".jpeg"]:
            content_type = "image/jpeg"
        elif path.suffix.lower() == ".png":
            content_type = "image/png"
        elif path.suffix.lower() == ".pdf":
            content_type = "application/pdf"

        # Get original filename (remove .encrypted extension if present)
        filename = path.name
        if filename.endswith(".encrypted"):
            filename = filename[:-10]  # Remove .encrypted extension

        return Response(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {e}",
        )
