"""Add user presence table

Revision ID: 20251219_0001
Revises: 20251218_profile_settings
Create Date: 2025-12-19

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251219_0001"
down_revision = "20251218_profile_settings"
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Upgrade database schema."""
    # Create user_presence table (only if it doesn't exist)
    if not table_exists("user_presence"):
        op.create_table(
            "user_presence",
            sa.Column(
                "id",
                sa.String(length=36),
                nullable=False,
                comment="User ID (primary key)",
            ),
            sa.Column(
                "is_online",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
                comment="User online status",
            ),
            sa.Column(
                "last_seen_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
                comment="Last activity timestamp",
            ),
            sa.Column(
                "connection_count",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
                comment="Number of active connections",
            ),
            sa.Column(
                "status_message",
                sa.String(length=200),
                nullable=True,
                comment="Optional status message",
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["id"], ["user.id"], ondelete="CASCADE"),
        )
        # Create index on is_online for efficient online friends queries
        op.create_index(
            op.f("ix_user_presence_is_online"),
            "user_presence",
            ["is_online"],
            unique=False,
        )


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop user_presence table
    op.drop_index(op.f("ix_user_presence_is_online"), table_name="user_presence")
    op.drop_table("user_presence")
