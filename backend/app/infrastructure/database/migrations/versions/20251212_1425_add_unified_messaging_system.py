"""add_unified_messaging_system

Revision ID: b1a4a2b9ed17
Revises: 6464e740a297
Create Date: 2025-12-12 14:25:43.645904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1a4a2b9ed17'
down_revision: Union[str, None] = '6464e740a297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create chat_rooms table (unified for all chat types)
    op.create_table(
        "chat_rooms",
        sa.Column("room_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),

        # Room type
        sa.Column("room_type", sa.String(20), nullable=False),  # 'direct', 'team', 'matching'

        # Room information
        sa.Column("room_name", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),

        # Type-specific metadata (JSON)
        sa.Column("metadata", sa.JSON(), nullable=True),

        # Display settings
        sa.Column("display_mode", sa.String(10), nullable=True),  # 'open', 'blind'

        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default="false"),

        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("last_message_at", sa.TIMESTAMP(), nullable=True),
    )

    # Create indexes for chat_rooms
    op.create_index("idx_chat_rooms_type", "chat_rooms", ["room_type"])
    op.create_index("idx_chat_rooms_active", "chat_rooms", ["is_active"])
    op.create_index("idx_chat_rooms_last_message", "chat_rooms", ["last_message_at"], postgresql_ops={"last_message_at": "DESC"})
    op.execute("CREATE INDEX idx_chat_rooms_metadata ON chat_rooms USING GIN (metadata)")

    # 2. Create chat_members table (unified for all participants)
    op.create_table(
        "chat_members",
        sa.Column("member_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("room_id", sa.UUID(), sa.ForeignKey("chat_rooms.room_id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),

        # Member role
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),  # 'owner', 'admin', 'member'

        # Display name (for matching blind mode)
        sa.Column("display_name", sa.String(50), nullable=True),
        sa.Column("anonymous_name", sa.String(20), nullable=True),  # 'A1', 'B2'

        # Group identification (for matching)
        sa.Column("group_label", sa.String(10), nullable=True),  # 'A', 'B'
        sa.Column("member_index", sa.Integer(), nullable=True),

        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_muted", sa.Boolean(), nullable=False, server_default="false"),

        # Read status
        sa.Column("last_read_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("unread_count", sa.Integer(), nullable=False, server_default="0"),

        # Timestamps
        sa.Column("joined_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("left_at", sa.TIMESTAMP(), nullable=True),

        sa.UniqueConstraint("room_id", "user_id", name="uq_chat_members_room_user"),
    )

    # Create indexes for chat_members
    op.create_index("idx_chat_members_room", "chat_members", ["room_id"])
    op.create_index("idx_chat_members_user", "chat_members", ["user_id"])
    op.create_index("idx_chat_members_active", "chat_members", ["is_active"])

    # 3. Create chat_messages table (unified for all messages)
    op.create_table(
        "chat_messages",
        sa.Column("message_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("room_id", sa.UUID(), sa.ForeignKey("chat_rooms.room_id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),

        # Message content
        sa.Column("message_type", sa.String(20), nullable=False, server_default="text"),  # 'text', 'image', 'file', 'system'
        sa.Column("content", sa.Text(), nullable=False),

        # Attachments
        sa.Column("attachments", sa.ARRAY(sa.Text()), nullable=True),

        # Reply/Thread
        sa.Column("parent_message_id", sa.UUID(), sa.ForeignKey("chat_messages.message_id", ondelete="SET NULL"), nullable=True),
        sa.Column("thread_count", sa.Integer(), nullable=False, server_default="0"),

        # Reactions (JSON)
        sa.Column("reactions", sa.JSON(), nullable=False, server_default="[]"),

        # Status
        sa.Column("is_edited", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),

        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=True),
    )

    # Create indexes for chat_messages
    op.create_index("idx_chat_messages_room", "chat_messages", ["room_id"])
    op.create_index("idx_chat_messages_sender", "chat_messages", ["sender_id"])
    op.create_index("idx_chat_messages_created", "chat_messages", ["created_at"], postgresql_ops={"created_at": "DESC"})
    op.create_index("idx_chat_messages_parent", "chat_messages", ["parent_message_id"])


def downgrade() -> None:
    # Drop indexes and tables in reverse order

    # Messages
    op.drop_index("idx_chat_messages_parent", table_name="chat_messages")
    op.drop_index("idx_chat_messages_created", table_name="chat_messages")
    op.drop_index("idx_chat_messages_sender", table_name="chat_messages")
    op.drop_index("idx_chat_messages_room", table_name="chat_messages")
    op.drop_table("chat_messages")

    # Members
    op.drop_index("idx_chat_members_active", table_name="chat_members")
    op.drop_index("idx_chat_members_user", table_name="chat_members")
    op.drop_index("idx_chat_members_room", table_name="chat_members")
    op.drop_table("chat_members")

    # Rooms
    op.execute("DROP INDEX IF EXISTS idx_chat_rooms_metadata")
    op.drop_index("idx_chat_rooms_last_message", table_name="chat_rooms")
    op.drop_index("idx_chat_rooms_active", table_name="chat_rooms")
    op.drop_index("idx_chat_rooms_type", table_name="chat_rooms")
    op.drop_table("chat_rooms")

