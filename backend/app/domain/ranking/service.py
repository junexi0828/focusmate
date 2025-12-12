"""Ranking service for business logic."""

import secrets
import string
from typing import Optional
from uuid import UUID

from app.domain.ranking.schemas import (
    TeamCreate,
    TeamInvitationCreate,
    TeamResponse,
    TeamUpdate,
)
from app.infrastructure.repositories.ranking_repository import RankingRepository


class RankingService:
    """Service for ranking business logic."""

    def __init__(self, repository: RankingRepository):
        """Initialize service with repository."""
        self.repository = repository

    def _generate_invite_code(self, length: int = 8) -> str:
        """Generate a random invite code."""
        characters = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(characters) for _ in range(length))

    async def create_team(self, team_data: TeamCreate, leader_id: str) -> TeamResponse:
        """Create a new ranking team."""
        # Generate unique invite code
        invite_code = self._generate_invite_code()

        team_dict = {
            "team_name": team_data.team_name,
            "team_type": team_data.team_type,
            "leader_id": leader_id,
            "mini_game_enabled": team_data.mini_game_enabled,
            "invite_code": invite_code,
            "affiliation_info": team_data.affiliation_info,
        }

        team = await self.repository.create_team(team_dict)

        # Add leader as team member
        await self.repository.add_team_member(
            {
                "team_id": team.team_id,
                "user_id": leader_id,
                "role": "leader",
            }
        )

        return TeamResponse.model_validate(team)

    async def get_team(self, team_id: UUID) -> Optional[TeamResponse]:
        """Get team by ID."""
        team = await self.repository.get_team_by_id(team_id)
        if not team:
            return None
        return TeamResponse.model_validate(team)

    async def update_team(
        self, team_id: UUID, update_data: TeamUpdate, user_id: str
    ) -> Optional[TeamResponse]:
        """Update team information (leader only)."""
        # Verify user is team leader
        team = await self.repository.get_team_by_id(team_id)
        if not team or team.leader_id != user_id:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        updated_team = await self.repository.update_team(team_id, update_dict)

        if not updated_team:
            return None

        return TeamResponse.model_validate(updated_team)

    async def delete_team(self, team_id: UUID, user_id: str) -> bool:
        """Delete team (leader only)."""
        # Verify user is team leader
        team = await self.repository.get_team_by_id(team_id)
        if not team or team.leader_id != user_id:
            return False

        return await self.repository.delete_team(team_id)

    async def get_user_teams(self, user_id: str) -> list[TeamResponse]:
        """Get all teams a user is a member of."""
        teams = await self.repository.get_user_teams(user_id)
        return [TeamResponse.model_validate(team) for team in teams]

    async def get_all_teams(self) -> list[TeamResponse]:
        """Get all teams (admin only)."""
        teams = await self.repository.get_all_teams()
        return [TeamResponse.model_validate(team) for team in teams]

    async def invite_member(
        self, team_id: UUID, invitation_data: TeamInvitationCreate, inviter_id: str
    ) -> dict:
        """Invite a new member to the team."""
        # Verify inviter is team leader
        team = await self.repository.get_team_by_id(team_id)
        if not team or team.leader_id != inviter_id:
            raise ValueError("Only team leader can invite members")

        # Check team member count (minimum 4, recommended max 8)
        members = await self.repository.get_team_members(team_id)
        if len(members) >= 8:
            raise ValueError("Team has reached maximum capacity (8 members)")

        invitation_dict = {
            "team_id": team_id,
            "email": invitation_data.email,
            "invited_by": inviter_id,
        }

        invitation = await self.repository.create_invitation(invitation_dict)

        return {
            "invitation_id": invitation.invitation_id,
            "team_id": team_id,
            "email": invitation.email,
            "status": invitation.status,
            "expires_at": invitation.expires_at,
        }

    async def accept_invitation(self, invitation_id: UUID, user_id: str) -> bool:
        """Accept a team invitation."""
        invitation = await self.repository.get_invitation_by_id(invitation_id)
        if not invitation or invitation.status != "pending":
            return False

        # Check if invitation has expired
        from datetime import datetime

        if invitation.expires_at < datetime.utcnow():
            await self.repository.update_invitation_status(invitation_id, "expired")
            return False

        # Check if user is already a member
        existing_member = await self.repository.get_member_by_user_and_team(
            user_id, invitation.team_id
        )
        if existing_member:
            return False

        # Add user as team member
        await self.repository.add_team_member(
            {
                "team_id": invitation.team_id,
                "user_id": user_id,
                "role": "member",
            }
        )

        # Update invitation status
        await self.repository.update_invitation_status(invitation_id, "accepted")

        return True

    async def reject_invitation(self, invitation_id: UUID) -> bool:
        """Reject a team invitation."""
        invitation = await self.repository.get_invitation_by_id(invitation_id)
        if not invitation or invitation.status != "pending":
            return False

        await self.repository.update_invitation_status(invitation_id, "rejected")
        return True

    async def leave_team(self, team_id: UUID, user_id: str) -> bool:
        """Leave a team."""
        # Check if user is team leader
        team = await self.repository.get_team_by_id(team_id)
        if not team:
            return False

        if team.leader_id == user_id:
            # Leader cannot leave, must delete team or transfer leadership
            return False

        return await self.repository.remove_team_member(user_id, team_id)

    async def remove_member(self, team_id: UUID, user_id: str, leader_id: str) -> bool:
        """Remove a member from team (leader only)."""
        # Verify requester is team leader
        team = await self.repository.get_team_by_id(team_id)
        if not team or team.leader_id != leader_id:
            return False

        # Cannot remove leader
        if user_id == leader_id:
            return False

        return await self.repository.remove_team_member(user_id, team_id)

    # Verification methods
    async def submit_verification_request(
        self, team_id: UUID, documents: dict, user_id: str
    ) -> dict:
        """Submit a verification request for a team."""
        # Verify user is team leader
        team = await self.repository.get_team_by_id(team_id)
        if not team or team.leader_id != user_id:
            raise ValueError("Only team leader can submit verification request")

        # Check if team already has pending or approved request
        existing_request = await self.repository.get_verification_request_by_team(
            team_id
        )
        if existing_request and existing_request.status in ["pending", "approved"]:
            raise ValueError(
                f"Team already has a {existing_request.status} verification request"
            )

        # Create verification request
        request_data = {
            "team_id": team_id,
            "documents": documents,
            "status": "pending",
        }

        request = await self.repository.create_verification_request(request_data)

        return {
            "request_id": request.request_id,
            "team_id": team_id,
            "status": request.status,
            "submitted_at": request.submitted_at,
        }

    async def get_verification_status(self, team_id: UUID) -> Optional[dict]:
        """Get verification status for a team."""
        request = await self.repository.get_verification_request_by_team(team_id)
        if not request:
            return None

        return {
            "request_id": request.request_id,
            "team_id": team_id,
            "status": request.status,
            "submitted_at": request.submitted_at,
            "reviewed_at": request.reviewed_at,
            "admin_note": request.admin_note,
        }

    async def get_pending_verifications(self) -> list[dict]:
        """Get all pending verification requests (admin only)."""
        requests = await self.repository.get_pending_verification_requests()

        results = []
        for request in requests:
            team = await self.repository.get_team_by_id(request.team_id)
            results.append(
                {
                    "request_id": request.request_id,
                    "team_id": request.team_id,
                    "team_name": team.team_name if team else "Unknown",
                    "team_type": team.team_type if team else "Unknown",
                    "documents": request.documents,
                    "submitted_at": request.submitted_at,
                }
            )

        return results

    async def review_verification(
        self, request_id: UUID, approved: bool, admin_note: str, admin_id: str
    ) -> bool:
        """Review a verification request (admin only)."""
        from datetime import datetime

        request = await self.repository.get_verification_request_by_id(request_id)
        if not request or request.status != "pending":
            return False

        # Update verification request
        update_data = {
            "status": "approved" if approved else "rejected",
            "admin_note": admin_note,
            "reviewed_at": datetime.utcnow(),
            "reviewed_by": admin_id,
        }

        updated_request = await self.repository.update_verification_request(
            request_id, update_data
        )

        if not updated_request:
            return False

        # Update team verification status
        if approved:
            await self.repository.update_team(
                request.team_id, {"verification_status": "verified"}
            )
        else:
            await self.repository.update_team(
                request.team_id, {"verification_status": "rejected"}
            )

        return True

    # Email notification integration
    async def _send_verification_notification(
        self, team_id: UUID, status: str, admin_note: Optional[str] = None
    ) -> None:
        """Send email notification for verification status change."""
        from app.infrastructure.email.email_service import email_service

        team = await self.repository.get_team_by_id(team_id)
        if not team:
            return

        # TODO: Get leader email from user service
        leader_email = f"leader_{team.leader_id}@example.com"  # Placeholder

        if status == "pending":
            await email_service.send_verification_submitted_email(
                team.team_name, leader_email
            )
        elif status == "approved":
            await email_service.send_verification_approved_email(
                team.team_name, leader_email, admin_note
            )
        elif status == "rejected":
            await email_service.send_verification_rejected_email(
                team.team_name, leader_email, admin_note
            )

    # Session methods
    async def start_session(
        self, team_id: UUID, user_id: str, session_type: str = "work"
    ) -> dict:
        """Start a ranking session."""
        # Verify user is team member
        member = await self.repository.get_member_by_user_and_team(user_id, team_id)
        if not member:
            raise ValueError("User is not a member of this team")

        # Session will be created when completed
        return {
            "team_id": team_id,
            "user_id": user_id,
            "session_type": session_type,
            "message": "Session started. Complete it to record.",
        }

    async def complete_session(
        self,
        team_id: UUID,
        user_id: str,
        duration_minutes: int,
        session_type: str = "work",
        success: bool = True,
    ) -> dict:
        """Complete a ranking session and record it."""
        # Verify user is team member
        member = await self.repository.get_member_by_user_and_team(user_id, team_id)
        if not member:
            raise ValueError("User is not a member of this team")

        # Create session record
        session_data = {
            "team_id": team_id,
            "user_id": user_id,
            "duration_minutes": duration_minutes,
            "session_type": session_type,
            "success": success,
        }

        session = await self.repository.create_session(session_data)

        return {
            "session_id": session.session_id,
            "team_id": team_id,
            "user_id": user_id,
            "duration_minutes": duration_minutes,
            "session_type": session_type,
            "success": success,
            "completed_at": session.completed_at,
        }

    async def get_team_statistics(self, team_id: UUID) -> dict:
        """Get team statistics."""
        stats = await self.repository.get_team_stats(team_id)

        # Get member count
        members = await self.repository.get_team_members(team_id)

        # Calculate streak (simplified - just check if there are sessions today)
        from datetime import datetime, timedelta

        today = datetime.utcnow().date()
        sessions_today = await self.repository.get_team_sessions(team_id, limit=1000)
        sessions_today_count = sum(
            1 for s in sessions_today if s.completed_at.date() == today and s.success
        )

        return {
            "team_id": team_id,
            "total_focus_time": stats["total_focus_time"],
            "total_sessions": stats["total_sessions"],
            "member_count": len(members),
            "current_streak": 1 if sessions_today_count > 0 else 0,  # Simplified
        }

    async def get_session_history(
        self, team_id: UUID, user_id: Optional[str] = None, limit: int = 100
    ) -> list[dict]:
        """Get session history for a team or user."""
        if user_id:
            sessions = await self.repository.get_user_sessions(user_id, team_id, limit)
        else:
            sessions = await self.repository.get_team_sessions(team_id, limit)

        return [
            {
                "session_id": s.session_id,
                "team_id": s.team_id,
                "user_id": s.user_id,
                "duration_minutes": s.duration_minutes,
                "session_type": s.session_type,
                "success": s.success,
                "completed_at": s.completed_at,
            }
            for s in sessions
        ]

    # Mini-game methods
    async def start_mini_game(
        self, team_id: UUID, user_id: str, game_type: str
    ) -> dict:
        """Start a mini-game session."""
        # Verify user is team member
        member = await self.repository.get_member_by_user_and_team(user_id, team_id)
        if not member:
            raise ValueError("User is not a member of this team")

        # Validate game type
        valid_games = ["dino_jump", "dot_collector", "snake"]
        if game_type not in valid_games:
            raise ValueError(f"Invalid game type. Must be one of: {valid_games}")

        return {
            "team_id": team_id,
            "user_id": user_id,
            "game_type": game_type,
            "message": "Game started. Submit score when finished.",
        }

    async def submit_mini_game_score(
        self,
        team_id: UUID,
        user_id: str,
        game_type: str,
        score: int,
        completion_time: int,
    ) -> dict:
        """Submit mini-game score."""
        # Verify user is team member
        member = await self.repository.get_member_by_user_and_team(user_id, team_id)
        if not member:
            raise ValueError("User is not a member of this team")

        # Validate score (basic anti-cheat)
        if score < 0 or score > 999999:
            raise ValueError("Invalid score")

        if completion_time < 1 or completion_time > 3600:  # Max 1 hour
            raise ValueError("Invalid completion time")

        # Create game record
        game_data = {
            "team_id": team_id,
            "user_id": user_id,
            "game_type": game_type,
            "score": score,
            "completion_time": completion_time,
        }

        game = await self.repository.create_mini_game(game_data)

        return {
            "game_id": game.game_id,
            "team_id": team_id,
            "user_id": user_id,
            "game_type": game_type,
            "score": score,
            "completion_time": completion_time,
            "played_at": game.played_at,
        }

    async def get_mini_game_leaderboard(
        self, game_type: str, limit: int = 10
    ) -> list[dict]:
        """Get leaderboard for a specific game type."""
        return await self.repository.get_mini_game_leaderboard(game_type, limit)

    async def get_team_mini_game_history(
        self, team_id: UUID, game_type: Optional[str] = None, limit: int = 50
    ) -> list[dict]:
        """Get mini-game history for a team."""
        games = await self.repository.get_team_mini_games(team_id, game_type, limit)

        return [
            {
                "game_id": g.game_id,
                "team_id": g.team_id,
                "user_id": g.user_id,
                "game_type": g.game_type,
                "score": g.score,
                "completion_time": g.completion_time,
                "played_at": g.played_at,
            }
            for g in games
        ]

    # Leaderboard methods
    async def get_hall_of_fame(self, period: str = "all") -> dict:
        """Get Hall of Fame leaderboard data."""
        # Validate period
        valid_periods = ["weekly", "monthly", "all"]
        if period not in valid_periods:
            raise ValueError(f"Invalid period. Must be one of: {valid_periods}")

        # Get comprehensive data
        teams = await self.repository.get_comprehensive_leaderboard(period)

        # Sort by total focus time
        teams_by_focus = sorted(
            teams, key=lambda x: x["total_focus_time"], reverse=True
        )

        # Sort by game score
        teams_by_games = sorted(
            teams, key=lambda x: x["total_game_score"], reverse=True
        )

        return {
            "period": period,
            "total_teams": len(teams),
            "teams": teams,
            "top_focus_teams": teams_by_focus[:10],
            "top_game_teams": teams_by_games[:10],
        }
