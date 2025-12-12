"""Ranking System ORM Models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin


class RankingTeam(Base, TimestampMixin):
    """Ranking team model.

    Attributes:
        team_id: Unique team identifier (UUID)
        team_name: Team name
        team_type: Type of team (general, department, lab, club)
        verification_status: School verification status
        leader_id: Team leader user ID
        mini_game_enabled: Whether mini-games are enabled
        invite_code: Unique invite code for joining
        affiliation_info: School/department information (JSONB)
    """

    __tablename__ = "ranking_teams"

    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        comment="Unique team identifier",
    )

    team_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Team name",
    )

    team_type: Mapped[str] = mapped_column(
        Enum("general", "department", "lab", "club", name="ranking_team_type"),
        nullable=False,
        comment="Type of team",
    )

    verification_status: Mapped[str] = mapped_column(
        Enum("none", "pending", "verified", "rejected", name="ranking_verification_status"),
        nullable=False,
        server_default="none",
        comment="School verification status",
    )

    leader_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Team leader user ID",
    )

    mini_game_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Mini-games enabled",
    )

    invite_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        unique=True,
        nullable=True,
        comment="Unique invite code",
    )

    affiliation_info: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="School/department information",
    )

    def __repr__(self) -> str:
        """String representation of RankingTeam."""
        return f"<RankingTeam(team_id={self.team_id}, team_name={self.team_name}, type={self.team_type})>"


class RankingTeamMember(Base):
    """Ranking team member model.

    Attributes:
        member_id: Unique member record identifier
        team_id: Team identifier
        user_id: User identifier
        role: Member role (leader, member)
        joined_at: Timestamp when member joined
    """

    __tablename__ = "ranking_team_members"

    member_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        comment="Unique member record identifier",
    )

    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ranking_teams.team_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Team identifier",
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User identifier",
    )

    role: Mapped[str] = mapped_column(
        Enum("leader", "member", name="ranking_member_role"),
        nullable=False,
        server_default="member",
        comment="Member role",
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        comment="Join timestamp",
    )

    def __repr__(self) -> str:
        """String representation of RankingTeamMember."""
        return f"<RankingTeamMember(member_id={self.member_id}, team_id={self.team_id}, user_id={self.user_id})>"


class RankingTeamInvitation(Base):
    """Ranking team invitation model.

    Attributes:
        invitation_id: Unique invitation identifier
        team_id: Team identifier
        email: Invitee email
        invited_by: Inviter user ID
        status: Invitation status (pending, accepted, rejected, expired)
        created_at: Creation timestamp
        expires_at: Expiration timestamp
        accepted_at: Acceptance timestamp (optional)
    """

    __tablename__ = "ranking_team_invitations"

    invitation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        comment="Unique invitation identifier",
    )

    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ranking_teams.team_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Team identifier",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Invitee email",
    )

    invited_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        comment="Inviter user ID",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
        index=True,
        comment="Invitation status",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        comment="Creation timestamp",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Expiration timestamp",
    )

    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Acceptance timestamp",
    )

    def __repr__(self) -> str:
        """String representation of RankingTeamInvitation."""
        return f"<RankingTeamInvitation(invitation_id={self.invitation_id}, email={self.email}, status={self.status})>"


class RankingSession(Base):
    """Ranking session model.

    Attributes:
        session_id: Unique session identifier
        team_id: Team identifier
        user_id: User identifier
        duration_minutes: Session duration in minutes
        session_type: Session type (work, break)
        success: Whether session was successful
        completed_at: Completion timestamp
    """

    __tablename__ = "ranking_sessions"

    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        comment="Unique session identifier",
    )

    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ranking_teams.team_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Team identifier",
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User identifier",
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Session duration in minutes",
    )

    session_type: Mapped[str] = mapped_column(
        Enum("work", "break", name="ranking_session_type"),
        nullable=False,
        index=True,
        comment="Session type",
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Session success status",
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        index=True,
        comment="Completion timestamp",
    )

    def __repr__(self) -> str:
        """String representation of RankingSession."""
        return f"<RankingSession(session_id={self.session_id}, team_id={self.team_id}, duration={self.duration_minutes})>"


class RankingMiniGame(Base):
    """Ranking mini-game model.

    Attributes:
        game_id: Unique game identifier
        team_id: Team identifier
        user_id: User identifier
        game_type: Game type (quiz, reaction, memory)
        score: Game score
        success: Whether game was successful
        completion_time: Completion time in seconds
        game_data: Game-specific data (JSONB)
        played_at: Play timestamp
    """

    __tablename__ = "ranking_mini_games"

    game_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        comment="Unique game identifier",
    )

    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ranking_teams.team_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Team identifier",
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User identifier",
    )

    game_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Game type",
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="Game score",
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="Game success status",
    )

    completion_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Completion time in seconds",
    )

    game_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Game-specific data",
    )

    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        index=True,
        comment="Play timestamp",
    )

    def __repr__(self) -> str:
        """String representation of RankingMiniGame."""
        return f"<RankingMiniGame(game_id={self.game_id}, game_type={self.game_type}, score={self.score})>"


class RankingVerificationRequest(Base):
    """Ranking verification request model.

    Attributes:
        request_id: Unique request identifier
        team_id: Team identifier
        documents: Verification documents (JSONB)
        status: Request status (pending, approved, rejected)
        admin_note: Admin review note
        submitted_at: Submission timestamp
        reviewed_at: Review timestamp (optional)
        reviewed_by: Reviewer user ID (optional)
    """

    __tablename__ = "ranking_verification_requests"

    request_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        comment="Unique request identifier",
    )

    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ranking_teams.team_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Team identifier",
    )

    documents: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Verification documents",
    )

    status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", name="ranking_verification_request_status"),
        nullable=False,
        server_default="pending",
        index=True,
        comment="Request status",
    )

    admin_note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Admin review note",
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        comment="Submission timestamp",
    )

    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Review timestamp",
    )

    reviewed_by: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reviewer user ID",
    )

    def __repr__(self) -> str:
        """String representation of RankingVerificationRequest."""
        return f"<RankingVerificationRequest(request_id={self.request_id}, team_id={self.team_id}, status={self.status})>"


class RankingLeaderboard(Base, TimestampMixin):
    """Ranking leaderboard cache model.

    Attributes:
        leaderboard_id: Unique leaderboard entry identifier
        team_id: Team identifier
        ranking_type: Ranking type (study_time, streak, mini_game)
        period: Ranking period (weekly, monthly, all_time)
        score: Ranking score
        rank: Current rank
        rank_change: Rank change from previous period
    """

    __tablename__ = "ranking_leaderboard"

    leaderboard_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        comment="Unique leaderboard entry identifier",
    )

    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ranking_teams.team_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Team identifier",
    )

    ranking_type: Mapped[str] = mapped_column(
        Enum("study_time", "streak", "mini_game", name="ranking_leaderboard_type"),
        nullable=False,
        comment="Ranking type",
    )

    period: Mapped[str] = mapped_column(
        Enum("weekly", "monthly", "all_time", name="ranking_period"),
        nullable=False,
        comment="Ranking period",
    )

    score: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default="0",
        comment="Ranking score",
    )

    rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Current rank",
    )

    rank_change: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default="0",
        comment="Rank change from previous period",
    )

    def __repr__(self) -> str:
        """String representation of RankingLeaderboard."""
        return f"<RankingLeaderboard(team_id={self.team_id}, type={self.ranking_type}, period={self.period}, rank={self.rank})>"
