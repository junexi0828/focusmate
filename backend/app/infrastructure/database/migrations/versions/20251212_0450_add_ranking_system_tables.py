"""add_ranking_system_tables

Revision ID: 97fc315f3aeb
Revises: ce4607683d8e
Create Date: 2025-12-12 04:50:57.263804

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "97fc315f3aeb"
down_revision: Union[str, None] = "ce4607683d8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLAlchemy will automatically create ENUM types when creating tables
    # No need to manually create them

    # 1. ranking_teams table
    op.create_table(
        "ranking_teams",
        sa.Column("team_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_name", sa.String(100), nullable=False),
        sa.Column("team_type", sa.Enum("general", "department", "lab", "club", name="ranking_team_type"), nullable=False),
        sa.Column(
            "verification_status",
            sa.Enum("none", "pending", "verified", "rejected", name="ranking_verification_status"),
            nullable=False,
            server_default="none",
        ),
        sa.Column("leader_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mini_game_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("invite_code", sa.String(10), unique=True),
        sa.Column("affiliation_info", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_ranking_teams_leader", "ranking_teams", ["leader_id"])
    op.create_index("idx_ranking_teams_type", "ranking_teams", ["team_type"])
    op.create_index("idx_ranking_teams_status", "ranking_teams", ["verification_status"])

    # 2. ranking_team_members table
    op.create_table(
        "ranking_team_members",
        sa.Column("member_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ranking_teams.team_id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("leader", "member", name="ranking_member_role"), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_ranking_team_members_team", "ranking_team_members", ["team_id"])
    op.create_index("idx_ranking_team_members_user", "ranking_team_members", ["user_id"])
    op.create_unique_constraint("uq_ranking_team_user", "ranking_team_members", ["team_id", "user_id"])

    # 3. ranking_team_invitations table
    op.create_table(
        "ranking_team_invitations",
        sa.Column("invitation_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ranking_teams.team_id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("invited_by", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),  # pending, accepted, rejected, expired
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_ranking_invitations_team", "ranking_team_invitations", ["team_id"])
    op.create_index("idx_ranking_invitations_email", "ranking_team_invitations", ["email"])
    op.create_index("idx_ranking_invitations_status", "ranking_team_invitations", ["status"])

    # 4. ranking_sessions table
    op.create_table(
        "ranking_sessions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ranking_teams.team_id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("session_type", sa.Enum("work", "break", name="ranking_session_type"), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_ranking_sessions_team", "ranking_sessions", ["team_id"])
    op.create_index("idx_ranking_sessions_user", "ranking_sessions", ["user_id"])
    op.create_index("idx_ranking_sessions_completed", "ranking_sessions", ["completed_at"])
    op.create_index("idx_ranking_sessions_type", "ranking_sessions", ["session_type"])

    # 5. ranking_mini_games table
    op.create_table(
        "ranking_mini_games",
        sa.Column("game_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ranking_teams.team_id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("game_type", sa.String(50), nullable=False),  # quiz, reaction, memory
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("success", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completion_time", sa.Float(), nullable=True),  # seconds
        sa.Column("game_data", postgresql.JSONB(), nullable=True),  # question, answer, etc.
        sa.Column("played_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_ranking_mini_games_team", "ranking_mini_games", ["team_id"])
    op.create_index("idx_ranking_mini_games_user", "ranking_mini_games", ["user_id"])
    op.create_index("idx_ranking_mini_games_type", "ranking_mini_games", ["game_type"])
    op.create_index("idx_ranking_mini_games_played", "ranking_mini_games", ["played_at"])

    # 6. ranking_verification_requests table
    op.create_table(
        "ranking_verification_requests",
        sa.Column("request_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ranking_teams.team_id", ondelete="CASCADE"), nullable=False),
        sa.Column("documents", postgresql.JSONB(), nullable=False),  # [{type, url, user_id}]
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", name="ranking_verification_request_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(36), sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("idx_ranking_verification_team", "ranking_verification_requests", ["team_id"])
    op.create_index("idx_ranking_verification_status", "ranking_verification_requests", ["status"])

    # 7. ranking_leaderboard table (cache)
    op.create_table(
        "ranking_leaderboard",
        sa.Column("leaderboard_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ranking_teams.team_id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "ranking_type",
            sa.Enum("study_time", "streak", "mini_game", name="ranking_leaderboard_type"),
            nullable=False,
        ),
        sa.Column("period", sa.Enum("weekly", "monthly", "all_time", name="ranking_period"), nullable=False),
        sa.Column("score", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("rank_change", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_ranking_leaderboard_team", "ranking_leaderboard", ["team_id"])
    op.create_index("idx_ranking_leaderboard_type_period", "ranking_leaderboard", ["ranking_type", "period"])
    op.create_index("idx_ranking_leaderboard_rank", "ranking_leaderboard", ["rank"])
    op.create_unique_constraint("uq_ranking_leaderboard", "ranking_leaderboard", ["team_id", "ranking_type", "period"])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("ranking_leaderboard")
    op.drop_table("ranking_verification_requests")
    op.drop_table("ranking_mini_games")
    op.drop_table("ranking_sessions")
    op.drop_table("ranking_team_invitations")
    op.drop_table("ranking_team_members")
    op.drop_table("ranking_teams")

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS ranking_period")
    op.execute("DROP TYPE IF EXISTS ranking_leaderboard_type")
    op.execute("DROP TYPE IF EXISTS ranking_verification_request_status")
    op.execute("DROP TYPE IF EXISTS ranking_session_type")
    op.execute("DROP TYPE IF EXISTS ranking_member_role")
    op.execute("DROP TYPE IF EXISTS ranking_verification_status")
    op.execute("DROP TYPE IF EXISTS ranking_team_type")
