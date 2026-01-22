"""add_refresh_tokens_table

Revision ID: 20260108_1355
Revises: 20260105_0009
Create Date: 2026-01-08 13:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260108_1355"
down_revision = "20260105_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table already exists to prevent duplicate creation
    from sqlalchemy import inspect
    from alembic import context

    conn = context.get_bind()
    inspector = inspect(conn)

    if 'refresh_tokens' in inspector.get_table_names():
        print("⚠️ refresh_tokens table already exists, skipping creation")
        return

    op.create_table(
        "refresh_tokens",
        sa.Column(
            "id",
            sa.String(length=36),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "last_rotated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("device_info", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
            name=op.f("fk_refresh_tokens_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
    )

    op.create_index(
        "idx_refresh_tokens_user_id", "refresh_tokens", ["user_id"]
    )
    op.create_index(
        "idx_refresh_tokens_token_id", "refresh_tokens", ["token_id"], unique=True
    )
    op.create_index(
        "idx_refresh_tokens_family_id", "refresh_tokens", ["family_id"]
    )


def downgrade() -> None:
    op.drop_index("idx_refresh_tokens_family_id", table_name="refresh_tokens")
    op.drop_index("idx_refresh_tokens_token_id", table_name="refresh_tokens")
    op.drop_index("idx_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
