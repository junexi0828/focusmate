"""add_performance_indexes

Revision ID: (auto-generated)
Revises: (auto-generated)
Create Date: 2026-01-05 00:09:xx

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260105_0009'
down_revision: Union[str, None] = '1b6ce548b5b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes and total_points column."""

    # ========================================
    # PART 1: Add total_points column to ranking_teams
    # ========================================
    op.add_column(
        'ranking_teams',
        sa.Column('total_points', sa.Integer(), server_default='0', nullable=False, comment='Total points accumulated by the team')
    )

    # Backfill total_points from ranking_leaderboard
    op.execute("""
        UPDATE ranking_teams rt
        SET total_points = COALESCE(
            (SELECT SUM(score)::INTEGER
             FROM ranking_leaderboard rl
             WHERE rl.team_id = rt.team_id),
            0
        )
    """)

    # ========================================
    # PART 2: Create Performance Indexes
    # ========================================

    # 1. session_history indexes
    op.create_index(
        op.f("ix_session_history_completed_at"),
        "session_history",
        ["completed_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_session_history_room_id"),
        "session_history",
        ["room_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_session_history_session_type"),
        "session_history",
        ["session_type"],
        unique=False,
    )

    op.create_index(
        "ix_session_history_user_completed",
        "session_history",
        ["user_id", "completed_at"],
        unique=False,
    )

    # 2. notifications indexes
    op.create_index(
        op.f("ix_notifications_is_read"),
        "notifications",
        ["is_read"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_created_at"),
        "notifications",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_type"),
        "notifications",
        ["type"],
        unique=False,
    )

    op.create_index(
        "ix_notifications_user_unread",
        "notifications",
        ["user_id", "is_read", "created_at"],
        unique=False,
    )

    # 3. chat_messages indexes
    op.create_index(
        op.f("ix_chat_messages_room_id"),
        "chat_messages",
        ["room_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_chat_messages_sender_id"),
        "chat_messages",
        ["sender_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_chat_messages_created_at"),
        "chat_messages",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        "ix_chat_messages_room_created",
        "chat_messages",
        ["room_id", "created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_chat_messages_is_deleted"),
        "chat_messages",
        ["is_deleted"],
        unique=False,
    )

    # 4. chat_rooms indexes
    op.create_index(
        op.f("ix_chat_rooms_room_type"),
        "chat_rooms",
        ["room_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_chat_rooms_is_active"),
        "chat_rooms",
        ["is_active"],
        unique=False,
    )

    op.create_index(
        op.f("ix_chat_rooms_last_message_at"),
        "chat_rooms",
        ["last_message_at"],
        unique=False,
    )

    op.create_index(
        "ix_chat_rooms_type_active",
        "chat_rooms",
        ["room_type", "is_active", "last_message_at"],
        unique=False,
    )

    # 5. chat_members indexes
    op.create_index(
        op.f("ix_chat_members_user_id"),
        "chat_members",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_chat_members_is_active"),
        "chat_members",
        ["is_active"],
        unique=False,
    )

    op.create_index(
        "ix_chat_members_user_active",
        "chat_members",
        ["user_id", "is_active"],
        unique=False,
    )

    # 6. ranking_teams indexes
    op.create_index(
        op.f("ix_ranking_teams_team_name"),
        "ranking_teams",
        ["team_name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ranking_teams_team_type"),
        "ranking_teams",
        ["team_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ranking_teams_verification_status"),
        "ranking_teams",
        ["verification_status"],
        unique=False,
    )

    # Index for total_points (for leaderboard sorting)
    op.create_index(
        op.f('ix_ranking_teams_total_points'),
        'ranking_teams',
        ['total_points'],
        unique=False,
    )


def downgrade() -> None:
    """Remove performance indexes and total_points column."""

    # Drop indexes first
    op.drop_index(op.f('ix_ranking_teams_total_points'), table_name='ranking_teams')
    op.drop_index(op.f("ix_ranking_teams_verification_status"), table_name="ranking_teams")
    op.drop_index(op.f("ix_ranking_teams_team_type"), table_name="ranking_teams")
    op.drop_index(op.f("ix_ranking_teams_team_name"), table_name="ranking_teams")

    op.drop_index("ix_chat_members_user_active", table_name="chat_members")
    op.drop_index(op.f("ix_chat_members_is_active"), table_name="chat_members")
    op.drop_index(op.f("ix_chat_members_user_id"), table_name="chat_members")

    op.drop_index("ix_chat_rooms_type_active", table_name="chat_rooms")
    op.drop_index(op.f("ix_chat_rooms_last_message_at"), table_name="chat_rooms")
    op.drop_index(op.f("ix_chat_rooms_is_active"), table_name="chat_rooms")
    op.drop_index(op.f("ix_chat_rooms_room_type"), table_name="chat_rooms")

    op.drop_index(op.f("ix_chat_messages_is_deleted"), table_name="chat_messages")
    op.drop_index("ix_chat_messages_room_created", table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_created_at"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_sender_id"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_room_id"), table_name="chat_messages")

    op.drop_index("ix_notifications_user_unread", table_name="notifications")
    op.drop_index(op.f("ix_notifications_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_created_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_is_read"), table_name="notifications")

    op.drop_index("ix_session_history_user_completed", table_name="session_history")
    op.drop_index(op.f("ix_session_history_session_type"), table_name="session_history")
    op.drop_index(op.f("ix_session_history_room_id"), table_name="session_history")
    op.drop_index(op.f("ix_session_history_completed_at"), table_name="session_history")

    # Drop total_points column
    op.drop_column('ranking_teams', 'total_points')
