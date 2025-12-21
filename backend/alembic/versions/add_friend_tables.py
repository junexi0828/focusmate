"""Add friend tables

Revision ID: add_friend_tables
Revises:
Create Date: 2025-12-18

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "add_friend_tables"
down_revision = None  # Set to the previous revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create friend_request table
    op.create_table(
        "friend_request",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sender_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("receiver_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.Enum("pending", "accepted", "rejected", name="friend_request_status"), nullable=False, server_default="pending"),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # Create friend table
    op.create_table(
        "friend",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("friend_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("is_blocked", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # Create unique constraint to prevent duplicate friend requests
    op.create_index("idx_friend_request_sender_receiver", "friend_request", ["sender_id", "receiver_id"], unique=False)

    # Create unique constraint to prevent duplicate friendships
    op.create_index("idx_friend_user_friend", "friend", ["user_id", "friend_id"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_friend_user_friend", table_name="friend")
    op.drop_index("idx_friend_request_sender_receiver", table_name="friend_request")
    op.drop_table("friend")
    op.drop_table("friend_request")

    # Drop enum type
    sa.Enum(name="friend_request_status").drop(op.get_bind(), checkfirst=True)
