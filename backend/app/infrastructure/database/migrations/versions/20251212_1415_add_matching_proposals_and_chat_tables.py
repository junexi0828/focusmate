"""add_matching_proposals_and_chat_tables

Revision ID: 6464e740a297
Revises: 4f3801f6629c
Create Date: 2025-12-12 14:15:53.690878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6464e740a297'
down_revision: Union[str, None] = '4f3801f6629c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create matching_proposals table
    op.create_table(
        "matching_proposals",
        sa.Column("proposal_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pool_id_a", sa.UUID(), sa.ForeignKey("matching_pools.pool_id", ondelete="CASCADE"), nullable=False),
        sa.Column("pool_id_b", sa.UUID(), sa.ForeignKey("matching_pools.pool_id", ondelete="CASCADE"), nullable=False),

        # Acceptance status
        sa.Column("group_a_status", sa.String(20), nullable=False, server_default="pending"),  # pending, accepted, rejected
        sa.Column("group_b_status", sa.String(20), nullable=False, server_default="pending"),

        # Final status
        sa.Column("final_status", sa.String(20), nullable=False, server_default="pending"),  # pending, matched, rejected

        # Chat room (when matched)
        sa.Column("chat_room_id", sa.UUID(), nullable=True),

        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("expires_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP + INTERVAL '24 hours'")),
        sa.Column("matched_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),

        sa.UniqueConstraint("pool_id_a", "pool_id_b", name="uq_matching_proposals_pools"),
    )

    # Create indexes for proposals
    op.create_index("idx_matching_proposals_status", "matching_proposals", ["final_status"])
    op.create_index("idx_matching_proposals_pool_a", "matching_proposals", ["pool_id_a"])
    op.create_index("idx_matching_proposals_pool_b", "matching_proposals", ["pool_id_b"])

    # 2. Create matching_chat_rooms table
    op.create_table(
        "matching_chat_rooms",
        sa.Column("room_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("proposal_id", sa.UUID(), sa.ForeignKey("matching_proposals.proposal_id", ondelete="CASCADE"), nullable=False, unique=True),

        # Room information
        sa.Column("room_name", sa.String(200), nullable=False),
        sa.Column("display_mode", sa.String(10), nullable=False),  # blind, open

        # Group information (JSON)
        sa.Column("group_a_info", sa.JSON(), nullable=False),
        sa.Column("group_b_info", sa.JSON(), nullable=False),

        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),

        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # Create indexes for chat rooms
    op.create_index("idx_matching_chat_rooms_proposal", "matching_chat_rooms", ["proposal_id"])
    op.create_index("idx_matching_chat_rooms_active", "matching_chat_rooms", ["is_active"])

    # 3. Create matching_chat_members table
    op.create_table(
        "matching_chat_members",
        sa.Column("member_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("room_id", sa.UUID(), sa.ForeignKey("matching_chat_rooms.room_id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),

        # Group identification
        sa.Column("group_label", sa.String(10), nullable=False),  # A, B
        sa.Column("member_index", sa.Integer(), nullable=False),  # 1, 2, 3...

        # Anonymous name (blind mode)
        sa.Column("anonymous_name", sa.String(20), nullable=True),  # A1, A2, B1, B2...

        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_read_at", sa.TIMESTAMP(), nullable=True),

        # Timestamps
        sa.Column("joined_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("left_at", sa.TIMESTAMP(), nullable=True),

        sa.UniqueConstraint("room_id", "user_id", name="uq_matching_chat_members_room_user"),
    )

    # Create indexes for chat members
    op.create_index("idx_matching_chat_members_room", "matching_chat_members", ["room_id"])
    op.create_index("idx_matching_chat_members_user", "matching_chat_members", ["user_id"])

    # 4. Create matching_messages table
    op.create_table(
        "matching_messages",
        sa.Column("message_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("room_id", sa.UUID(), sa.ForeignKey("matching_chat_rooms.room_id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),

        # Message content
        sa.Column("message_type", sa.String(20), nullable=False, server_default="text"),  # text, image, system
        sa.Column("content", sa.Text(), nullable=False),

        # Attachments
        sa.Column("attachments", sa.ARRAY(sa.Text()), nullable=True),

        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=True),
    )

    # Create indexes for messages
    op.create_index("idx_matching_messages_room", "matching_messages", ["room_id"])
    op.create_index("idx_matching_messages_created", "matching_messages", ["created_at"], postgresql_ops={"created_at": "DESC"})
    op.create_index("idx_matching_messages_sender", "matching_messages", ["sender_id"])


def downgrade() -> None:
    # Drop indexes and tables in reverse order

    # Messages
    op.drop_index("idx_matching_messages_sender", table_name="matching_messages")
    op.drop_index("idx_matching_messages_created", table_name="matching_messages")
    op.drop_index("idx_matching_messages_room", table_name="matching_messages")
    op.drop_table("matching_messages")

    # Chat members
    op.drop_index("idx_matching_chat_members_user", table_name="matching_chat_members")
    op.drop_index("idx_matching_chat_members_room", table_name="matching_chat_members")
    op.drop_table("matching_chat_members")

    # Chat rooms
    op.drop_index("idx_matching_chat_rooms_active", table_name="matching_chat_rooms")
    op.drop_index("idx_matching_chat_rooms_proposal", table_name="matching_chat_rooms")
    op.drop_table("matching_chat_rooms")

    # Proposals
    op.drop_index("idx_matching_proposals_pool_b", table_name="matching_proposals")
    op.drop_index("idx_matching_proposals_pool_a", table_name="matching_proposals")
    op.drop_index("idx_matching_proposals_status", table_name="matching_proposals")
    op.drop_table("matching_proposals")

