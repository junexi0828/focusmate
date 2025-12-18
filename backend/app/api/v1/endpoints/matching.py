"""API endpoints for matching pools."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DatabaseSession, get_current_user
from app.domain.matching.schemas import (
    ComprehensiveMatchingStats,
    MatchingPoolCreate,
    MatchingPoolResponse,
    MatchingPoolStats,
)
from app.domain.matching.optimized_service import OptimizedMatchingPoolService
from app.infrastructure.repositories.matching_pool_repository import (
    MatchingPoolRepository,
)
from app.infrastructure.repositories.verification_repository import (
    VerificationRepository,
)

router = APIRouter(prefix="/matching", tags=["matching"])


def get_matching_pool_service(
    db: DatabaseSession,
) -> OptimizedMatchingPoolService:
    """Get optimized matching pool service dependency."""
    pool_repository = MatchingPoolRepository(db)
    verification_repository = VerificationRepository(db)
    return OptimizedMatchingPoolService(pool_repository, verification_repository)


# Matching Pool Endpoints
@router.post("/pools", status_code=status.HTTP_201_CREATED)
async def create_matching_pool(
    data: MatchingPoolCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[
        OptimizedMatchingPoolService, Depends(get_matching_pool_service)
    ],
) -> MatchingPoolResponse:
    """Create a new matching pool."""
    try:
        return await service.create_pool(current_user["id"], data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/pools/my")
async def get_my_matching_pool(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[
        OptimizedMatchingPoolService, Depends(get_matching_pool_service)
    ],
) -> Optional[MatchingPoolResponse]:
    """Get current user's active matching pool."""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        pool = await service.get_my_pool(current_user["id"])
        return pool
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get matching pool: {str(e)}",
        )


@router.get("/pools/stats")
async def get_pool_statistics(
    service: Annotated[
        OptimizedMatchingPoolService, Depends(get_matching_pool_service)
    ],
) -> MatchingPoolStats:
    """Get matching pool statistics."""
    try:
        return await service.get_pool_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pool statistics: {str(e)}",
        )


@router.get("/pools/{pool_id}")
async def get_matching_pool(
    pool_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[
        OptimizedMatchingPoolService, Depends(get_matching_pool_service)
    ],
) -> MatchingPoolResponse:
    """Get matching pool by ID."""
    pool = await service.get_pool(pool_id, current_user["id"])
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found"
        )
    return pool


@router.delete("/pools/{pool_id}")
async def cancel_matching_pool(
    pool_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[
        OptimizedMatchingPoolService, Depends(get_matching_pool_service)
    ],
) -> dict:
    """Cancel a matching pool."""
    try:
        success = await service.cancel_pool(pool_id, current_user["id"])
        if success:
            return {"message": "매칭 풀이 취소되었습니다."}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/stats/comprehensive")
async def get_comprehensive_statistics(
    service: Annotated[
        OptimizedMatchingPoolService, Depends(get_matching_pool_service)
    ],
) -> ComprehensiveMatchingStats:
    """Get comprehensive matching statistics including pools and proposals."""
    try:
        return await service.get_comprehensive_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comprehensive statistics: {str(e)}",
        )
