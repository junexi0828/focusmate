"""Authentication and User Profile API endpoints."""


from typing import Annotated
from datetime import UTC, datetime
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, Response, status

from app.api.deps import get_current_user, get_current_user_required
from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.security import validate_refresh_token
from app.domain.user.schemas import (
    NaverOAuthCallback,
    PasswordResetComplete,
    PasswordResetRequest,
    PasswordResetVerify,
    TokenResponse,
    UserLogin,
    UserProfileUpdate,
    UserRegister,
    UserResponse,
)
from app.domain.user.service import UserService
from app.infrastructure.database.session import DatabaseSession
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.redis.session_helpers import clear_user_activity


router = APIRouter(prefix="/auth", tags=["auth"])


def _require_self_or_admin(current_user: dict, user_id: str) -> None:
    """Allow only the user or an admin to access the resource."""
    if current_user["id"] != user_id and not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )


def get_user_repository(db: DatabaseSession) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)


def get_user_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Get user service."""
    return UserService(repo)


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserRegister,
    service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    """Register a new user."""
    try:
        return await service.register(data)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Registration error: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later.",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    data: UserLogin,
    service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    """Login user and return JWT token."""
    try:
        token_response = await service.login(data)
        if token_response.refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=token_response.refresh_token,
                httponly=True,
                secure=settings.is_production,
                samesite="lax",
                path="/",
                max_age=7 * 24 * 60 * 60,
            )
            token_response.refresh_token = None
        return token_response
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Login error: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later.",
        )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: DatabaseSession,
) -> dict:
    """Logout user and revoke refresh token."""
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = validate_refresh_token(refresh_token)
            token_id = payload["jti"]
            user_id = payload["sub"]

            refresh_token_repo = RefreshTokenRepository(db)
            db_token = await refresh_token_repo.get_by_token_id(token_id)
            if db_token:
                db_token.expires_at = datetime.now(UTC)
                await refresh_token_repo.update(db_token)

            await clear_user_activity(user_id, token_id)
        except Exception:
            pass

    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Logged out successfully"}


@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_profile(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Get user profile by ID.

    Args:
        user_id: User identifier
        service: User service

    Returns:
        User profile with stats

    Raises:
        HTTPException: If user not found
    """
    try:
        _require_self_or_admin(current_user, user_id)
        return await service.get_profile(user_id)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/profile/{user_id}", response_model=UserResponse)
async def update_profile(
    user_id: str,
    data: UserProfileUpdate,
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Update user profile.

    Args:
        user_id: User identifier
        data: Profile updates (username, bio, school, profile_image)
        service: User service

    Returns:
        Updated user profile

    Raises:
        HTTPException: If user not found
    """
    try:
        _require_self_or_admin(current_user, user_id)
        return await service.update_profile(user_id, data)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/profile/{user_id}/upload-image", status_code=status.HTTP_200_OK)
async def upload_profile_image(
    user_id: str,
    file: UploadFile = File(...),
    current_user: Annotated[dict, Depends(get_current_user_required)],
    service: Annotated[UserService, Depends(get_user_service)] = None,
) -> dict:
    """Upload user profile image.

    Args:
        user_id: User identifier
        file: Image file to upload
        current_user: Current authenticated user
        service: User service

    Returns:
        Response with image URL

    Raises:
        HTTPException: If user not found or unauthorized
    """
    from app.infrastructure.storage.file_upload import FileUploadService

    # Verify user is updating their own profile
    _require_self_or_admin(current_user, user_id)

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    # Upload file
    upload_service = FileUploadService()
    try:
        file_path = await upload_service.save_file(file, f"profile/{user_id}")
        file_url = upload_service.get_file_url(file_path)

        # Update user profile with image URL
        await service.update_profile(user_id, UserProfileUpdate(profile_image=file_url))

        return {"profile_image": file_url}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/password-reset/request")
async def request_password_reset(
    data: PasswordResetRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    """Request password reset.

    Args:
        data: Password reset request with email
        service: User service

    Returns:
        Success message (always returns success to prevent email enumeration)
    """
    try:
        return await service.request_password_reset(data)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/password-reset/verify")
async def verify_password_reset_token(
    data: PasswordResetVerify,
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    """Verify password reset token.

    Args:
        data: Token verification data
        service: User service

    Returns:
        Token validity status
    """
    try:
        return await service.verify_password_reset_token(data)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/password-reset/complete")
async def complete_password_reset(
    data: PasswordResetComplete,
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    """Complete password reset.

    Args:
        data: Password reset completion data
        service: User service

    Returns:
        Success message
    """
    try:
        return await service.complete_password_reset(data)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/naver/login")
async def naver_login_url() -> dict:
    """Get Naver OAuth login URL.

    Returns:
        Naver OAuth authorization URL
    """
    import secrets

    from app.core.config import settings

    state = secrets.token_urlsafe(32)
    naver_auth_url = (
        f"https://nid.naver.com/oauth2.0/authorize?"
        f"response_type=code&"
        f"client_id={settings.NAVER_CLIENT_ID}&"
        f"redirect_uri={settings.NAVER_REDIRECT_URI}&"
        f"state={state}&"
        f"scope=email"
    )

    return {
        "auth_url": naver_auth_url,
        "state": state,
    }


@router.post("/naver/callback", response_model=TokenResponse)
async def naver_oauth_callback(
    data: NaverOAuthCallback,
    service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    """Handle Naver OAuth callback.

    Args:
        data: Naver OAuth callback data
        service: User service

    Returns:
        Token response with user data
    """
    try:
        return await service.naver_oauth_login(data)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/naver/unlink", status_code=status.HTTP_200_OK)
async def naver_oauth_unlink(
    naver_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    """Handle Naver OAuth unlink/disconnect callback.

    This endpoint is called by Naver when a user disconnects their Naver account
    or withdraws from Naver membership.

    Args:
        naver_id: Naver OAuth ID (from Naver callback)
        service: User service

    Returns:
        Success message
    """
    try:
        return await service.naver_oauth_unlink(naver_id)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Naver unlink error: {e!s}", exc_info=True)
        # Always return success to Naver even if user not found
        return {"message": "Unlink processed"}
