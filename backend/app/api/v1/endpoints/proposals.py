"""API endpoints for matching proposals."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import DatabaseSession, get_current_user
from app.domain.matching.proposal_schemas import ProposalAction, ProposalResponse
from app.domain.matching.proposal_service import ProposalRepository, ProposalService
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.matching_pool_repository import (
    MatchingPoolRepository,
)

router = APIRouter(prefix="/matching/proposals", tags=["matching-proposals"])


def get_proposal_service(
    db: Annotated[DatabaseSession, Depends()]
) -> ProposalService:
    """Get proposal service dependency."""
    proposal_repo = ProposalRepository(db)
    pool_repo = MatchingPoolRepository(db)
    chat_repo = ChatRepository(db)
    return ProposalService(proposal_repo, pool_repo, chat_repo)


@router.get("/my", response_model=list[ProposalResponse])
async def get_my_proposals(
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ProposalService, Depends(get_proposal_service)] = None,
):
    """Get proposals for current user's pool."""
    return await service.get_my_proposals(current_user["id"])


@router.post("/{proposal_id}/respond")
async def respond_to_proposal(
    proposal_id: UUID,
    action: ProposalAction,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ProposalService, Depends(get_proposal_service)] = None,
) -> ProposalResponse:
    """Respond to a proposal (accept/reject)."""
    try:
        # Get user's pool
        pool_repo = MatchingPoolRepository(service.proposal_repo.session)
        pool = await pool_repo.get_user_active_pool(current_user["id"])

        if not pool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active pool found",
            )

        return await service.respond_to_proposal(
            proposal_id, pool.pool_id, action
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{proposal_id}")
async def get_proposal(
    proposal_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[ProposalService, Depends(get_proposal_service)] = None,
    include_pools: bool = Query(True, description="Include pool information in response"),
) -> ProposalResponse:
    """Get proposal details with optional pool information."""
    proposal = await service.proposal_repo.get_proposal_by_id(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    response = ProposalResponse.model_validate(proposal)

    # Include pool information if requested
    if include_pools:
        pool_a = await service.pool_repo.get_pool_by_id(proposal.pool_id_a)
        pool_b = await service.pool_repo.get_pool_by_id(proposal.pool_id_b)

        if pool_a:
            from app.domain.matching.schemas import MatchingPoolResponse
            response.pool_a = MatchingPoolResponse.model_validate(pool_a).model_dump()
        if pool_b:
            from app.domain.matching.schemas import MatchingPoolResponse
            response.pool_b = MatchingPoolResponse.model_validate(pool_b).model_dump()

    return response
