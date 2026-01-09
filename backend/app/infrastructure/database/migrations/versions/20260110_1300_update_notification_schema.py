"""update_notification_schema

Revision ID: 20260110_1300
Revises: 20260108_1355
Create Date: 2026-01-10 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260110_1300"
down_revision = "20260108_1355"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column(
        "notifications",
        sa.Column("priority", sa.String(length=20), server_default="medium", nullable=False)
    )
    op.add_column(
        "notifications",
        sa.Column("routing", sa.JSON(), nullable=True)
    )
    op.add_column(
        "notifications",
        sa.Column("group_key", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "notifications",
        sa.Column("delivered_via_ws", sa.Boolean(), server_default="false", nullable=False)
    )
    op.add_column(
        "notifications",
        sa.Column("delivered_via_email", sa.Boolean(), server_default="false", nullable=False)
    )

    # Remove server_default after creation for cleaner schema (optional but recommended for non-nulls)
    op.alter_column("notifications", "priority", server_default=None)
    op.alter_column("notifications", "delivered_via_ws", server_default=None)
    op.alter_column("notifications", "delivered_via_email", server_default=None)

    # Create indexes
    op.create_index(
        "idx_group_key", "notifications", ["group_key"]
    )
    op.create_index(
        "idx_user_unread", "notifications", ["user_id", "is_read"]
    )
    # Check if we need to create idx_user_created.
    # user_id is indexed, created_at might be implied but composite is better.
    op.create_index(
        "idx_user_created", "notifications", ["user_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("idx_user_created", table_name="notifications")
    op.drop_index("idx_user_unread", table_name="notifications")
    op.drop_index("idx_group_key", table_name="notifications")

    op.drop_column("notifications", "delivered_via_email")
    op.drop_column("notifications", "delivered_via_ws")
    op.drop_column("notifications", "group_key")
    op.drop_column("notifications", "routing")
    op.drop_column("notifications", "priority")
