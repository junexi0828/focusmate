"""Ranking API endpoints."""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from app.api.deps import DatabaseSession, get_current_user
from app.core.rbac import require_admin
from app.domain.ranking.schemas import (
    LeaderboardEntry,
    LeaderboardResponse,
    TeamCreate,
    TeamInvitationCreate,
    TeamInvitationResponse,
    TeamResponse,
    TeamUpdate,
)
from app.domain.ranking.service import RankingService
from app.domain.verification.schemas import VerificationResponse, VerificationReview
from app.infrastructure.repositories.ranking_repository import RankingRepository
from app.infrastructure.repositories.user_repository import UserRepository


router = APIRouter(prefix="/ranking", tags=["ranking"])


async def get_ranking_service(db: DatabaseSession) -> RankingService:
    """Dependency to get ranking service."""
    repository = RankingRepository(db)
    user_repository = UserRepository(db)
    return RankingService(repository, user_repository)


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
    try:
        # Admin can access all teams, regular users only their teams
        if current_user.get("is_admin"):
            # Return all teams for admin (or empty list if no teams exist)
            all_teams = await service.get_all_teams()
            return all_teams if all_teams else []
        return await service.get_user_teams(current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teams: {e!s}",
        )


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
        result = await service.invite_member(
            team_id, invitation_data, current_user["id"]
        )

        # Send invitation email
        try:
            from app.infrastructure.database.repositories.ranking_repository import (
                RankingRepository,
            )
            from app.infrastructure.database.repositories.user_repository import (
                UserRepository,
            )
            from app.infrastructure.database.session import get_db
            from app.services.email_service import email_service

            async for db in get_db():
                repo = RankingRepository(db)
                user_repo = UserRepository(db)

                team = await repo.get_team_by_id(team_id)
                inviter = await user_repo.get_by_id(current_user["id"])

                if team and inviter:
                    # Generate invitation link
                    invitation_link = f"https://focusmate.com/ranking/invitations/{result['invitation_id']}"

                    email_service.send_team_invitation(
                        to_email=invitation_data.email,
                        team_name=team.team_name,
                        inviter_name=inviter.username or inviter.email.split("@")[0],
                        invitation_link=invitation_link,
                    )
                break
        except Exception as e:
            import logging

            logging.exception(f"Failed to send invitation email: {e!s}")

        return result
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
        # Check if user is team leader
        team = await service.get_team(team_id)
        if team and team.leader_id == current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="팀 리더는 팀을 나갈 수 없습니다. 팀을 삭제하거나 리더를 양도해주세요.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="팀에서 나갈 수 없습니다.",
        )
    return {"message": "Left team successfully"}


# Leaderboard Endpoints
@router.get("/leaderboard")
async def get_leaderboard(
    service: Annotated[RankingService, Depends(get_ranking_service)],
    db: DatabaseSession,
    period: Literal["weekly", "monthly", "all_time"] = Query(
        "weekly", description="Period: weekly, monthly, all_time"
    ),
    limit: int = Query(50, ge=1, le=100, description="Number of teams to return"),
) -> dict:
    """Get leaderboard rankings for teams.

    Args:
        period: Time period (weekly, monthly, all_time)
        limit: Maximum number of teams to return

    Returns:
        Leaderboard with team rankings based on RankingSession data
    """

    try:
        from sqlalchemy import func, select

        from app.infrastructure.database.models.ranking import RankingMiniGame, RankingSession

        # Get all teams
        teams = await service.get_all_teams()

        if not teams:
            # Return empty leaderboard
            response = LeaderboardResponse(
                ranking_type="team",
                period=period,
                updated_at=datetime.now(UTC),
                leaderboard=[],
            )
            return response.model_dump()

        # Calculate date range based on period
        now = datetime.now(UTC)
        if period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            start_date = now - timedelta(days=30)
        else:  # all_time
            start_date = datetime.min.replace(tzinfo=UTC)

        # Calculate scores for each team based on RankingSession
        leaderboard_data = []
        for team in teams:
            # Calculate session stats from RankingSession table
            sessions_result = await db.execute(
                select(
                    func.sum(RankingSession.duration_minutes).label("total_minutes"),
                    func.count(RankingSession.session_id).label("total_sessions"),
                )
                .where(RankingSession.team_id == team.team_id)
                .where(RankingSession.completed_at >= start_date)
                .where(RankingSession.success == True)
                .where(RankingSession.session_type == "work")
            )
            session_stats = sessions_result.first()

            total_minutes = float(session_stats.total_minutes or 0)
            total_sessions = int(session_stats.total_sessions or 0)

            # Calculate mini-game score
            games_result = await db.execute(
                select(func.sum(RankingMiniGame.score).label("total_game_score"))
                .where(RankingMiniGame.team_id == team.team_id)
                .where(RankingMiniGame.played_at >= start_date)
            )
            game_stats = games_result.first()
            total_game_score = int(game_stats.total_game_score or 0)

            # Get member count
            from app.infrastructure.database.models.ranking import RankingTeamMember
            members_result = await db.execute(
                select(func.count(RankingTeamMember.member_id))
                .where(RankingTeamMember.team_id == team.team_id)
            )
            member_count = members_result.scalar() or 0

            # Calculate total score: focus time + session bonus + game score
            # Focus time in minutes + 5 points per session + game score / 10
            score = total_minutes + (total_sessions * 5) + (total_game_score / 10)
            average_score = score / member_count if member_count > 0 else 0.0

            leaderboard_data.append(
                {
                    "team": team,
                    "score": score,
                    "average_score": average_score,
                    "member_count": member_count,
                    "total_sessions": total_sessions,
                }
            )

        # Sort by score descending
        leaderboard_data.sort(key=lambda x: x["score"], reverse=True)

        # Get previous ranks from RankingLeaderboard cache
        from app.infrastructure.database.models.ranking import RankingLeaderboard
        previous_ranks = {}
        previous_ranks_result = await db.execute(
            select(RankingLeaderboard)
            .where(RankingLeaderboard.period == period)
            .where(RankingLeaderboard.ranking_type == "study_time")
        )
        for prev_rank in previous_ranks_result.scalars().all():
            previous_ranks[prev_rank.team_id] = prev_rank.rank

        # Create leaderboard entries with rank change calculation
        leaderboard_entries = []
        rank_changes_to_notify = []  # Track rank changes for notifications
        for idx, data in enumerate(leaderboard_data[:limit]):
            current_rank = idx + 1
            previous_rank = previous_ranks.get(data["team"].team_id)
            rank_change = 0
            if previous_rank is not None:
                rank_change = previous_rank - current_rank  # Positive = moved up, negative = moved down

            # Track significant rank changes for notifications
            if previous_rank is not None and abs(rank_change) >= 1:
                rank_changes_to_notify.append({
                    "team_id": data["team"].team_id,
                    "team_name": data["team"].team_name,
                    "previous_rank": previous_rank,
                    "current_rank": current_rank,
                    "rank_change": rank_change,
                })

            entry = LeaderboardEntry(
                rank=current_rank,
                team_id=data["team"].team_id,
                team_name=data["team"].team_name,
                team_type=data["team"].team_type,
                score=data["score"],
                rank_change=rank_change,
                member_count=data["member_count"],
                average_score=data["average_score"],
                total_sessions=data["total_sessions"],
            )
            leaderboard_entries.append(entry)

        # Update or create leaderboard cache entries
        for idx, data in enumerate(leaderboard_data[:limit]):
            current_rank = idx + 1
            # Check if entry exists
            existing_entry = await db.execute(
                select(RankingLeaderboard)
                .where(RankingLeaderboard.team_id == data["team"].team_id)
                .where(RankingLeaderboard.period == period)
                .where(RankingLeaderboard.ranking_type == "study_time")
            )
            existing = existing_entry.scalar_one_or_none()

            if existing:
                # Update existing entry
                previous_rank = existing.rank
                rank_change = previous_rank - current_rank if previous_rank else 0
                existing.rank = current_rank
                existing.score = float(data["score"])
                existing.rank_change = rank_change
            else:
                # Create new entry
                from app.infrastructure.database.models.ranking import RankingLeaderboard
                new_entry = RankingLeaderboard(
                    team_id=data["team"].team_id,
                    ranking_type="study_time",
                    period=period,
                    score=float(data["score"]),
                    rank=current_rank,
                    rank_change=0,
                )
                db.add(new_entry)

        await db.commit()

        # Send notifications for rank changes
        if rank_changes_to_notify:
            try:
                from app.domain.notification.service import NotificationService
                from app.infrastructure.repositories.notification_repository import (
                    NotificationRepository,
                )
                from app.infrastructure.repositories.ranking_repository import RankingRepository
                from app.infrastructure.repositories.user_repository import UserRepository

                notification_repo = NotificationRepository(db)
                ranking_repo = RankingRepository(db)
                user_repo = UserRepository(db)
                notification_service = NotificationService(notification_repo, user_repo)

                from app.domain.notification.schemas import NotificationCreate

                for change in rank_changes_to_notify:
                    # Get all team members
                    members = await ranking_repo.get_team_members(change["team_id"])
                    for member in members:
                        change_direction = "상승" if change["rank_change"] > 0 else "하락"
                        title = "랭킹 변동 알림"
                        message = (
                            f"{change['team_name']} 팀의 순위가 {change['previous_rank']}위에서 "
                            f"{change['current_rank']}위로 {change_direction}했습니다 "
                            f"({abs(change['rank_change'])}위 변동)"
                        )

                        notification_data = NotificationCreate(
                            user_id=member.user_id,
                            type="ranking",
                            title=title,
                            message=message,
                            data={
                                "team_id": str(change["team_id"]),
                                "team_name": change["team_name"],
                                "previous_rank": change["previous_rank"],
                                "current_rank": change["current_rank"],
                                "rank_change": change["rank_change"],
                                "period": period,
                            },
                        )
                        await notification_service.create_notification(notification_data)
            except Exception as e:
                # Log error but don't fail the request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send rank change notifications: {e!s}")

        response = LeaderboardResponse(
            ranking_type="team",
            period=period,
            updated_at=datetime.now(UTC),
            leaderboard=leaderboard_entries,
        )

        return response.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {e!s}",
        )


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


@router.get("/verifications/pending", response_model=list[VerificationResponse])
async def get_pending_verifications(
    current_user: Annotated[dict, Depends(require_admin)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> list[VerificationResponse]:
    """Get all pending verifications (Admin only)."""
    return await service.get_pending_verifications()


@router.post(
    "/verifications/{verification_id}/review", response_model=VerificationResponse
)
async def review_verification(
    verification_id: UUID,
    review: VerificationReview,
    current_user: Annotated[dict, Depends(require_admin)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> VerificationResponse:
    """Review a verification (Admin only)."""
    result = await service.review_verification(
        verification_id, review.status, review.admin_note
    )

    # Send email notification
    try:
        from app.infrastructure.database.repositories.ranking_repository import (
            RankingRepository,
        )
        from app.infrastructure.database.session import get_db
        from app.services.email_service import email_service

        # Get team and leader info
        async for db in get_db():
            repo = RankingRepository(db)
            verification = await repo.get_verification_by_id(verification_id)
            if verification and verification.team:
                team = verification.team
                leader = team.leader

                if review.status == "approved":
                    email_service.send_verification_approved(
                        to_email=leader.email,
                        team_name=team.team_name,
                        username=leader.username or leader.email.split("@")[0],
                    )
                elif review.status == "rejected":
                    email_service.send_verification_rejected(
                        to_email=leader.email,
                        team_name=team.team_name,
                        username=leader.username or leader.email.split("@")[0],
                        reason=review.admin_note,
                    )
            break
    except Exception as e:
        # Log error but don't fail the request
        import logging

        logging.exception(f"Failed to send verification email: {e!s}")

    return result


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
    user_id: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Get session history for a team or user."""
    return await service.get_session_history(team_id, user_id, limit)


@router.post("/teams/{team_id}/invite")
async def invite_member(
    team_id: str,
    data: TeamInvitationCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> TeamInvitationResponse:
    """Invite a member to the team."""
    try:
        invitation = await service.invite_member(team_id, current_user["id"], data)
        return invitation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/invitations")
async def get_user_invitations(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
    status_filter: str | None = Query(None, regex="^(pending|accepted|rejected)$"),
) -> dict:
    """Get all invitations for the current user."""
    try:
        invitations = await service.get_user_invitations(
            current_user["id"], status_filter
        )
        return {"invitations": invitations, "total": len(invitations)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve invitations: {e!s}",
        )


@router.get("/teams/{team_id}/members")
async def get_team_members(
    team_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
) -> dict:
    """Get all members of a team."""
    try:
        members = await service.get_team_members(team_id, current_user["id"])
        return {"members": members, "total": len(members)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# Mini-Game Endpoints
@router.post("/mini-games/start", status_code=status.HTTP_201_CREATED)
async def start_mini_game(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
    team_id: UUID = Query(..., description="Team ID"),
    game_type: str = Query(
        ..., description="Game type: dino_jump, dot_collector, snake"
    ),
) -> dict:
    """Start a mini-game session."""
    try:
        return await service.start_mini_game(team_id, current_user["id"], game_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/mini-games/submit", status_code=status.HTTP_201_CREATED)
async def submit_mini_game_score(
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[RankingService, Depends(get_ranking_service)],
    team_id: UUID = Query(..., description="Team ID"),
    game_type: str = Query(
        ..., description="Game type: dino_jump, dot_collector, snake"
    ),
    score: int = Query(..., ge=0, le=999999, description="Game score"),
    completion_time: float = Query(
        ..., gt=0, le=3600, description="Completion time in seconds"
    ),
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
    game_type: str | None = None,
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
