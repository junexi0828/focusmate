"""Refresh token endpoint with smart session logic."""

from datetime import datetime, timedelta, UTC
from uuid import uuid4
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, validate_refresh_token
from app.core.exceptions import UnauthorizedException
from app.core.config import settings
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.redis.session_helpers import check_user_activity, store_token_mapping
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/refresh")
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token with smart session extension.

    Implements:
    - Token type validation
    - Absolute expiry check
    - Reuse detection (revoke family on theft)
    - Smart extension (activity-based)
    - Token rotation (24h cycle)
    - Redis failure handling (fail-open)
    """
    # 1. Extract token from cookie or header
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            refresh_token = auth_header[7:]

    if not refresh_token:
        raise HTTPException(401, "No refresh token")

    # 2. Validate token type & expiry
    try:
        payload = validate_refresh_token(refresh_token)
    except (ValueError, Exception) as e:
        raise HTTPException(401, str(e))

    token_id = payload["jti"]
    user_id = payload["sub"]
    family_id = payload["family_id"]

    # 3. Check DB token
    refresh_token_repo = RefreshTokenRepository(db)
    db_token = await refresh_token_repo.get_by_token_id(token_id)

    if not db_token:
        raise HTTPException(401, "Token not found")

    # REUSE DETECTION: If token already expired, it's a theft attempt
    if db_token.expires_at < datetime.now(UTC):
        logger.warning(f"Revoked token reused: {token_id}, revoking family {family_id}")
        await refresh_token_repo.revoke_family(family_id)
        raise HTTPException(401, "Token revoked - security event")

    # 4. Smart Extension Check (with Redis failure handling)
    is_active = False
    try:
        is_active = await check_user_activity(user_id, token_id)
    except Exception as e:
        # Fail-open: Allow refresh but don't extend DB expiry
        logger.warning(f"Redis unavailable during refresh: {e}")
        is_active = False

    # 5. Conditional DB Update (only if active AND near expiry)
    should_extend = is_active and (db_token.expires_at - datetime.now(UTC)) < timedelta(hours=24)

    if should_extend:
        new_expiry = min(
            datetime.now(UTC) + timedelta(days=7),
            db_token.absolute_expires_at
        )
        db_token.expires_at = new_expiry
        await refresh_token_repo.update(db_token)

    # 6. Rotation (if > 24h old) - FIX: Preserve expiry before revoking
    new_token_str = refresh_token
    if (datetime.now(UTC) - db_token.last_rotated_at) > timedelta(hours=24):
        # CRITICAL FIX: Save expiry BEFORE revoking
        preserved_expiry = db_token.expires_at
        preserved_absolute_expiry = db_token.absolute_expires_at

        # Revoke old token
        db_token.expires_at = datetime.now(UTC)
        await refresh_token_repo.update(db_token)

        # Create new token with preserved expiry
        new_db_token = await refresh_token_repo.create(
            user_id=user_id,
            family_id=family_id,
            expires_at=preserved_expiry,  # Use preserved value
            absolute_expires_at=preserved_absolute_expiry,
            device_info=db_token.device_info,
            ip_address=db_token.ip_address
        )
        new_token_str = create_refresh_token(user_id, new_db_token.token_id, family_id)
        try:
            await store_token_mapping(user_id, new_db_token.token_id)
        except Exception as e:
            logger.warning(f"Failed to update token mapping: {e}")

        # Update cookie
        response.set_cookie(
            key="refresh_token",
            value=new_token_str,
            httponly=True,
            secure=settings.is_production,
            samesite="lax",
            path="/",
            max_age=7*24*60*60
        )

    # 7. Issue new access token
    access_token = create_access_token({"sub": user_id})

    return {"access_token": access_token, "token_type": "bearer"}
