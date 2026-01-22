"""Add room invitation codes

Revision ID: 20251219_0002
Revises: 20251219_0001
Create Date: 2025-12-19

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251219_0002"
down_revision = "20251219_0001"
branch_labels = None
depends_on = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Upgrade database schema."""
    # Add invitation code fields to chat_rooms table
    if not column_exists("chat_rooms", "invitation_code"):
        op.add_column(
            "chat_rooms",
            sa.Column(
                "invitation_code",
                sa.String(length=8),
                nullable=True,
                comment="Room invitation code",
            ),
        )

    if not column_exists("chat_rooms", "invitation_expires_at"):
        op.add_column(
            "chat_rooms",
            sa.Column(
                "invitation_expires_at",
                sa.DateTime(timezone=True),
                nullable=True,
                comment="Invitation code expiration timestamp",
            ),
        )

    if not column_exists("chat_rooms", "invitation_max_uses"):
        op.add_column(
            "chat_rooms",
            sa.Column(
                "invitation_max_uses",
                sa.Integer(),
                nullable=True,
                comment="Maximum number of invitation uses",
            ),
        )

    if not column_exists("chat_rooms", "invitation_use_count"):
        op.add_column(
            "chat_rooms",
            sa.Column(
                "invitation_use_count",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
                comment="Current invitation use count",
            ),
        )

    # Create partial unique index on invitation_code (only for non-null values)
    try:
        op.create_index(
            "ix_chat_rooms_invitation_code",
            "chat_rooms",
            ["invitation_code"],
            unique=True,
            postgresql_where=sa.text("invitation_code IS NOT NULL"),
        )
    except Exception:
        # Index might already exist, skip
        pass

    # Create index on invitation_expires_at for cleanup queries
    try:
        op.create_index(
            op.f("ix_chat_rooms_invitation_expires_at"),
            "chat_rooms",
            ["invitation_expires_at"],
            unique=False,
        )
    except Exception:
        # Index might already exist, skip
        pass


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes
    try:
        op.drop_index(
            op.f("ix_chat_rooms_invitation_expires_at"), table_name="chat_rooms"
        )
    except Exception:
        pass

    try:
        op.drop_index("ix_chat_rooms_invitation_code", table_name="chat_rooms")
    except Exception:
        pass

    # Remove columns
    op.drop_column("chat_rooms", "invitation_use_count")
    op.drop_column("chat_rooms", "invitation_max_uses")
    op.drop_column("chat_rooms", "invitation_expires_at")
    op.drop_column("chat_rooms", "invitation_code")
