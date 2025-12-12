"""Ranking API endpoints."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile

from app.api.deps import DatabaseSession, get_current_user
from app.core.rbac import require_admin
from app.domain.ranking.schemas import (
    TeamCreate,
    TeamInvitationCreate,
    TeamResponse,
    TeamUpdate,
)
from app.domain.ranking.service import RankingService
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.ranking_repository import RankingRepository

router = APIRouter(prefix="/ranking", tags=["ranking"])


async def get_ranking_service(db: DatabaseSession) -> RankingService:
    """Dependency to get ranking service."""
    repository = RankingRepository(db)
    return RankingService(repository)


# Team Management Endpoints
@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> TeamResponse:
    """Create a new ranking team."""
    return await service.create_team(team_data, current_user["id"])


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> TeamResponse:
    """Get team by ID."""
    team = await service.get_team(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team


@router.get("/teams", response_model=list[TeamResponse])
async def get_my_teams(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> list[TeamResponse]:
    """Get all teams the current user is a member of."""
    # Admin can access all teams, regular users only their teams
    if current_user.get("is_admin"):
        # Return all teams for admin (or empty list if no teams exist)
        all_teams = await service.get_all_teams()
        return all_teams if all_teams else []
    return await service.get_user_teams(current_user["id"])


@router.patch("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    update_data: TeamUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> TeamResponse:
    """Update team information (leader only)."""
    team = await service.update_team(team_id, update_data, current_user["id"])
    if not team:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team leader can update team",
        )
    return team


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> None:
    """Delete team (leader only)."""
    success = await service.delete_team(team_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team leader can delete team",
        )


# Team Invitation Endpoints
@router.post("/teams/{team_id}/invite", status_code=status.HTTP_201_CREATED)
async def invite_member(
    team_id: UUID,
    invitation_data: TeamInvitationCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Invite a new member to the team (leader only)."""
    try:
        return await service.invite_member(team_id, invitation_data, current_user["id"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/teams/invitations/{invitation_id}/accept", status_code=status.HTTP_200_OK
)
async def accept_invitation(
    invitation_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Accept a team invitation."""
    success = await service.accept_invitation(invitation_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation",
        )
    return {"message": "Invitation accepted successfully"}


@router.post(
    "/teams/invitations/{invitation_id}/reject", status_code=status.HTTP_200_OK
)
async def reject_invitation(
    invitation_id: UUID,
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Reject a team invitation."""
    success = await service.reject_invitation(invitation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invitation"
        )
    return {"message": "Invitation rejected"}


@router.post("/teams/{team_id}/leave", status_code=status.HTTP_200_OK)
async def leave_team(
    team_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Leave a team."""
    success = await service.leave_team(team_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave team (leader must delete team or transfer leadership)",
        )
    return {"message": "Left team successfully"}


@router.delete(
    "/teams/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_member(
    team_id: UUID,
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> None:
    """Remove a member from team (leader only)."""
    success = await service.remove_member(team_id, user_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team leader can remove members",
        )


# Verification Endpoints
@router.post("/verification/request", status_code=status.HTTP_201_CREATED)
async def submit_verification_request(
    team_id: UUID,
    documents: list[dict],
    team_member_list: list[dict],
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Submit a verification request for a team (leader only)."""
    try:
        return await service.submit_verification_request(
            team_id,
            {"documents": documents, "team_member_list": team_member_list},
            current_user["id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/verification/status/{team_id}")
async def get_verification_status(
    team_id: UUID,
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Get verification status for a team."""
    status_info = await service.get_verification_status(team_id)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification request found for this team",
        )
    return status_info


@router.get("/admin/verification/pending")
async def get_pending_verifications(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> list[dict]:
    """Get all pending verification requests (admin only)."""
    # TODO: Add admin role check
    # if not current_user.get("is_admin"):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return await service.get_pending_verifications()


@router.post("/admin/verification/{request_id}/review", status_code=status.HTTP_200_OK)
async def review_verification(
    request_id: UUID,
    approved: bool,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
    admin_note: str = "",
) -> dict:
    """Review a verification request (admin only)."""
    # TODO: Add admin role check
    # if not current_user.get("is_admin"):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    success = await service.review_verification(
        request_id, approved, admin_note, current_user["id"]
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request or already reviewed",
        )

    return {
        "message": f"Verification request {'approved' if approved else 'rejected'} successfully"
    }


# File Upload Endpoint
@router.post("/verification/upload", status_code=status.HTTP_201_CREATED)
async def upload_verification_documents(
    team_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
    files: list[UploadFile],
) -> dict:
    """Upload verification documents (leader only)."""
    from app.infrastructure.storage.file_upload import FileUploadService

    # Verify user is team leader
    team = await service.get_team(team_id)
    if not team or team.leader_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team leader can upload documents",
        )

    # Upload files
    upload_service = FileUploadService()
    try:
        file_paths = await upload_service.save_multiple_files(files, str(team_id))
        file_urls = [upload_service.get_file_url(path) for path in file_paths]

        return {
            "team_id": team_id,
            "uploaded_files": file_urls,
            "count": len(file_urls),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Session Endpoints
@router.post("/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_session(
    team_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
    session_type: str = "work",
) -> dict:
    """Start a ranking session."""
    try:
        return await service.start_session(team_id, current_user["id"], session_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sessions/complete", status_code=status.HTTP_201_CREATED)
async def complete_session(
    team_id: UUID,
    duration_minutes: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
    session_type: str = "work",
    success: bool = True,
) -> dict:
    """Complete a ranking session."""
    try:
        return await service.complete_session(
            team_id, current_user["id"], duration_minutes, session_type, success
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/teams/{team_id}/stats")
async def get_team_stats(
    team_id: UUID,
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Get team statistics."""
    return await service.get_team_statistics(team_id)


@router.get("/teams/{team_id}/sessions")
async def get_session_history(
    team_id: UUID,
    service: Annotated[RankingService, Depends(get_ranking_service)],
    user_id: Optional[str] = None,
    limit: int = 100,
) -> list[dict]:
    """Get session history for a team or user."""
    return await service.get_session_history(team_id, user_id, limit)


# Mini-Game Endpoints
@router.post("/mini-games/start", status_code=status.HTTP_201_CREATED)
async def start_mini_game(
    team_id: UUID,
    game_type: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Start a mini-game session."""
    try:
        return await service.start_mini_game(team_id, current_user["id"], game_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/mini-games/submit", status_code=status.HTTP_201_CREATED)
async def submit_mini_game_score(
    team_id: UUID,
    game_type: str,
    score: int,
    completion_time: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Submit mini-game score."""
    try:
        return await service.submit_mini_game_score(
            team_id, current_user["id"], game_type, score, completion_time
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/mini-games/leaderboard/{game_type}")
async def get_mini_game_leaderboard(
    game_type: str,
    service: Annotated[RankingService, Depends(get_ranking_service)],
    limit: int = 10,
) -> list[dict]:
    """Get leaderboard for a specific game type."""
    try:
        return await service.get_mini_game_leaderboard(game_type, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/teams/{team_id}/mini-games")
async def get_team_mini_games(
    team_id: UUID,
    service: Annotated[RankingService, Depends(get_ranking_service)],
    game_type: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    """Get mini-game history for a team."""
    return await service.get_team_mini_game_history(team_id, game_type, limit)


# Hall of Fame Endpoints (Phase 5)
@router.get("/hall-of-fame")
async def get_hall_of_fame(
    service: Annotated[RankingService, Depends(get_ranking_service)],
    period: str = Query("all", description="Period: weekly, monthly, or all"),
) -> dict:
    """Get Hall of Fame leaderboard with comprehensive team statistics."""
    try:
        return await service.get_hall_of_fame(period)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
