"""Ranking repository for database operations."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.ranking import (
    RankingTeam,
    RankingTeamInvitation,
    RankingTeamMember,
)


class RankingRepository:
    """Repository for ranking database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    # Team operations
    async def create_team(self, team_data: dict) -> RankingTeam:
        """Create a new ranking team."""
        team = RankingTeam(**team_data)
        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)
        return team

    async def get_team_by_id(self, team_id: UUID) -> Optional[RankingTeam]:
        """Get team by ID."""
        result = await self.session.execute(
            select(RankingTeam).where(RankingTeam.team_id == team_id)
        )
        return result.scalar_one_or_none()

    async def get_teams_by_leader(self, leader_id: str) -> list[RankingTeam]:
        """Get all teams led by a user."""
        result = await self.session.execute(
            select(RankingTeam).where(RankingTeam.leader_id == leader_id)
        )
        return list(result.scalars().all())

    async def get_all_teams(self) -> list[RankingTeam]:
        """Get all teams (admin only)."""
        result = await self.session.execute(select(RankingTeam))
        return list(result.scalars().all())

    async def update_team(self, team_id: UUID, update_data: dict) -> Optional[RankingTeam]:
        """Update team information."""
        team = await self.get_team_by_id(team_id)
        if not team:
            return None

        for key, value in update_data.items():
            if value is not None:
                setattr(team, key, value)

        await self.session.commit()
        await self.session.refresh(team)
        return team

    async def delete_team(self, team_id: UUID) -> bool:
        """Delete a team."""
        team = await self.get_team_by_id(team_id)
        if not team:
            return False

        await self.session.delete(team)
        await self.session.commit()
        return True

    # Team member operations
    async def add_team_member(self, member_data: dict) -> RankingTeamMember:
        """Add a member to a team."""
        member = RankingTeamMember(**member_data)
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def get_team_members(self, team_id: UUID) -> list[RankingTeamMember]:
        """Get all members of a team."""
        result = await self.session.execute(
            select(RankingTeamMember).where(RankingTeamMember.team_id == team_id)
        )
        return list(result.scalars().all())

    async def get_member_by_user_and_team(
        self, user_id: str, team_id: UUID
    ) -> Optional[RankingTeamMember]:
        """Get team member by user ID and team ID."""
        result = await self.session.execute(
            select(RankingTeamMember).where(
                RankingTeamMember.user_id == user_id,
                RankingTeamMember.team_id == team_id,
            )
        )
        return result.scalar_one_or_none()

    async def remove_team_member(self, user_id: str, team_id: UUID) -> bool:
        """Remove a member from a team."""
        member = await self.get_member_by_user_and_team(user_id, team_id)
        if not member:
            return False

        await self.session.delete(member)
        await self.session.commit()
        return True

    async def get_user_teams(self, user_id: str) -> list[RankingTeam]:
        """Get all teams a user is a member of."""
        result = await self.session.execute(
            select(RankingTeam)
            .join(RankingTeamMember)
            .where(RankingTeamMember.user_id == user_id)
        )
        return list(result.scalars().all())

    # Team invitation operations
    async def create_invitation(self, invitation_data: dict) -> RankingTeamInvitation:
        """Create a team invitation."""
        # Set expiration to 7 days from now
        invitation_data["expires_at"] = datetime.utcnow() + timedelta(days=7)
        invitation = RankingTeamInvitation(**invitation_data)
        self.session.add(invitation)
        await self.session.commit()
        await self.session.refresh(invitation)
        return invitation

    async def get_invitation_by_id(self, invitation_id: UUID) -> Optional[RankingTeamInvitation]:
        """Get invitation by ID."""
        result = await self.session.execute(
            select(RankingTeamInvitation).where(
                RankingTeamInvitation.invitation_id == invitation_id
            )
        )
        return result.scalar_one_or_none()

    async def get_team_invitations(self, team_id: UUID) -> list[RankingTeamInvitation]:
        """Get all invitations for a team."""
        result = await self.session.execute(
            select(RankingTeamInvitation).where(RankingTeamInvitation.team_id == team_id)
        )
        return list(result.scalars().all())

    async def get_user_invitations(self, email: str) -> list[RankingTeamInvitation]:
        """Get all pending invitations for a user by email."""
        result = await self.session.execute(
            select(RankingTeamInvitation).where(
                RankingTeamInvitation.email == email,
                RankingTeamInvitation.status == "pending",
            )
        )
        return list(result.scalars().all())

    async def update_invitation_status(
        self, invitation_id: UUID, status: str
    ) -> Optional[RankingTeamInvitation]:
        """Update invitation status."""
        invitation = await self.get_invitation_by_id(invitation_id)
        if not invitation:
            return None

        invitation.status = status
        if status == "accepted":
            invitation.accepted_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(invitation)
        return invitation

    # Verification request operations
    async def create_verification_request(
        self, request_data: dict
    ) -> "RankingVerificationRequest":
        """Create a verification request."""
        from app.infrastructure.database.models.ranking import RankingVerificationRequest

        request = RankingVerificationRequest(**request_data)
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_verification_request_by_id(
        self, request_id: UUID
    ) -> Optional["RankingVerificationRequest"]:
        """Get verification request by ID."""
        from app.infrastructure.database.models.ranking import RankingVerificationRequest

        result = await self.session.execute(
            select(RankingVerificationRequest).where(
                RankingVerificationRequest.request_id == request_id
            )
        )
        return result.scalar_one_or_none()

    async def get_verification_request_by_team(
        self, team_id: UUID
    ) -> Optional["RankingVerificationRequest"]:
        """Get latest verification request for a team."""
        from app.infrastructure.database.models.ranking import RankingVerificationRequest

        result = await self.session.execute(
            select(RankingVerificationRequest)
            .where(RankingVerificationRequest.team_id == team_id)
            .order_by(RankingVerificationRequest.submitted_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_pending_verification_requests(
        self,
    ) -> list["RankingVerificationRequest"]:
        """Get all pending verification requests."""
        from app.infrastructure.database.models.ranking import RankingVerificationRequest

        result = await self.session.execute(
            select(RankingVerificationRequest)
            .where(RankingVerificationRequest.status == "pending")
            .order_by(RankingVerificationRequest.submitted_at.desc())
        )
        return list(result.scalars().all())

    async def update_verification_request(
        self, request_id: UUID, update_data: dict
    ) -> Optional["RankingVerificationRequest"]:
        """Update verification request."""

        request = await self.get_verification_request_by_id(request_id)
        if not request:
            return None

        for key, value in update_data.items():
            if value is not None:
                setattr(request, key, value)

        await self.session.commit()
        await self.session.refresh(request)
        return request

    # Session operations
    async def create_session(self, session_data: dict) -> "RankingSession":
        """Create a ranking session."""
        from app.infrastructure.database.models.ranking import RankingSession

        session = RankingSession(**session_data)
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def get_session_by_id(self, session_id: UUID) -> Optional["RankingSession"]:
        """Get session by ID."""
        from app.infrastructure.database.models.ranking import RankingSession

        result = await self.session.execute(
            select(RankingSession).where(RankingSession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_team_sessions(
        self, team_id: UUID, limit: int = 100
    ) -> list["RankingSession"]:
        """Get sessions for a team."""
        from app.infrastructure.database.models.ranking import RankingSession

        result = await self.session.execute(
            select(RankingSession)
            .where(RankingSession.team_id == team_id)
            .order_by(RankingSession.completed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_sessions(
        self, user_id: str, team_id: UUID, limit: int = 100
    ) -> list["RankingSession"]:
        """Get sessions for a user in a team."""
        from app.infrastructure.database.models.ranking import RankingSession

        result = await self.session.execute(
            select(RankingSession)
            .where(
                RankingSession.user_id == user_id,
                RankingSession.team_id == team_id,
            )
            .order_by(RankingSession.completed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_team_stats(self, team_id: UUID) -> dict:
        """Get team statistics."""
        from sqlalchemy import func
        from app.infrastructure.database.models.ranking import RankingSession

        # Total focus time
        total_result = await self.session.execute(
            select(func.sum(RankingSession.duration_minutes))
            .where(
                RankingSession.team_id == team_id,
                RankingSession.session_type == "work",
                RankingSession.success == True,
            )
        )
        total_focus_time = total_result.scalar() or 0

        # Total sessions
        count_result = await self.session.execute(
            select(func.count(RankingSession.session_id))
            .where(
                RankingSession.team_id == team_id,
                RankingSession.success == True,
            )
        )
        total_sessions = count_result.scalar() or 0

        return {
            "total_focus_time": float(total_focus_time),
            "total_sessions": int(total_sessions),
        }

    # Mini-game operations
    async def create_mini_game(self, game_data: dict) -> "RankingMiniGame":
        """Create a mini-game record."""
        from app.infrastructure.database.models.ranking import RankingMiniGame

        game = RankingMiniGame(**game_data)
        self.session.add(game)
        await self.session.commit()
        await self.session.refresh(game)
        return game

    async def get_mini_game_by_id(self, game_id: UUID) -> Optional["RankingMiniGame"]:
        """Get mini-game by ID."""
        from app.infrastructure.database.models.ranking import RankingMiniGame

        result = await self.session.execute(
            select(RankingMiniGame).where(RankingMiniGame.game_id == game_id)
        )
        return result.scalar_one_or_none()

    async def get_team_mini_games(
        self, team_id: UUID, game_type: Optional[str] = None, limit: int = 100
    ) -> list["RankingMiniGame"]:
        """Get mini-games for a team."""
        from app.infrastructure.database.models.ranking import RankingMiniGame

        query = select(RankingMiniGame).where(RankingMiniGame.team_id == team_id)

        if game_type:
            query = query.where(RankingMiniGame.game_type == game_type)

        query = query.order_by(RankingMiniGame.played_at.desc()).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_mini_game_leaderboard(
        self, game_type: str, limit: int = 10
    ) -> list[dict]:
        """Get leaderboard for a specific game type."""
        from sqlalchemy import func
        from app.infrastructure.database.models.ranking import RankingMiniGame, RankingTeam

        # Get top scores per team
        result = await self.session.execute(
            select(
                RankingMiniGame.team_id,
                RankingTeam.team_name,
                func.max(RankingMiniGame.score).label("best_score"),
                func.count(RankingMiniGame.game_id).label("games_played"),
            )
            .join(RankingTeam, RankingMiniGame.team_id == RankingTeam.team_id)
            .where(RankingMiniGame.game_type == game_type)
            .group_by(RankingMiniGame.team_id, RankingTeam.team_name)
            .order_by(func.max(RankingMiniGame.score).desc())
            .limit(limit)
        )

        return [
            {
                "team_id": row.team_id,
                "team_name": row.team_name,
                "best_score": int(row.best_score),
                "games_played": int(row.games_played),
            }
            for row in result
        ]

    # Leaderboard operations
    async def get_comprehensive_leaderboard(
        self, period: str = "all"
    ) -> list[dict]:
        """Get comprehensive leaderboard data for all teams."""
        from sqlalchemy import func
        from datetime import datetime, timedelta
        from app.infrastructure.database.models.ranking import (
            RankingTeam,
            RankingSession,
            RankingMiniGame,
        )

        # Calculate date filter
        date_filter = None
        if period == "weekly":
            date_filter = datetime.utcnow() - timedelta(days=7)
        elif period == "monthly":
            date_filter = datetime.utcnow() - timedelta(days=30)

        # Get session stats
        session_query = (
            select(
                RankingSession.team_id,
                func.sum(RankingSession.duration_minutes).label("total_focus_time"),
                func.count(RankingSession.session_id).label("session_count"),
            )
            .where(RankingSession.success == True)
            .group_by(RankingSession.team_id)
        )

        if date_filter:
            session_query = session_query.where(RankingSession.completed_at >= date_filter)

        session_result = await self.session.execute(session_query)
        session_stats = {row.team_id: row for row in session_result}

        # Get mini-game stats
        game_query = (
            select(
                RankingMiniGame.team_id,
                func.sum(RankingMiniGame.score).label("total_game_score"),
                func.count(RankingMiniGame.game_id).label("game_count"),
            )
            .group_by(RankingMiniGame.team_id)
        )

        if date_filter:
            game_query = game_query.where(RankingMiniGame.played_at >= date_filter)

        game_result = await self.session.execute(game_query)
        game_stats = {row.team_id: row for row in game_result}

        # Get all teams
        teams_result = await self.session.execute(
            select(RankingTeam).where(RankingTeam.verification_status == "verified")
        )
        teams = teams_result.scalars().all()

        # Combine data
        leaderboard = []
        for team in teams:
            session_data = session_stats.get(team.team_id)
            game_data = game_stats.get(team.team_id)

            leaderboard.append({
                "team_id": team.team_id,
                "team_name": team.team_name,
                "team_type": team.team_type,
                "total_focus_time": float(session_data.total_focus_time) if session_data else 0.0,
                "session_count": int(session_data.session_count) if session_data else 0,
                "total_game_score": int(game_data.total_game_score) if game_data else 0,
                "game_count": int(game_data.game_count) if game_data else 0,
            })

        return leaderboard
