"""add_matching_pools_table

Revision ID: 4f3801f6629c
Revises: 3f0e28052134
Create Date: 2025-12-12 13:42:53.860652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f3801f6629c'
down_revision: Union[str, None] = '3f0e28052134'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create matching_pools table
    op.create_table(
        "matching_pools",
        sa.Column("pool_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("creator_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),

        # Group information
        sa.Column("member_count", sa.Integer(), nullable=False),
        sa.Column("member_ids", sa.ARRAY(sa.Text()), nullable=False),

        # Department information (representative)
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("grade", sa.String(20), nullable=False),
        sa.Column("gender", sa.String(10), nullable=False),

        # Matching preferences
        sa.Column("preferred_match_type", sa.String(20), nullable=False),  # any, same_department, major_category
        sa.Column("preferred_categories", sa.ARRAY(sa.Text()), nullable=True),

        # Display settings
        sa.Column("matching_type", sa.String(10), nullable=False),  # blind, open

        # Message
        sa.Column("message", sa.Text(), nullable=True),

        # Status
        sa.Column("status", sa.String(20), nullable=False, server_default="waiting"),  # waiting, matched, expired, cancelled

        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("expires_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP + INTERVAL '7 days'")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),

        # Constraints
        sa.CheckConstraint("member_count >= 2 AND member_count <= 8", name="check_member_count"),
        sa.CheckConstraint("char_length(message) <= 200", name="check_message_length"),
    )

    # Create indexes
    op.create_index("idx_matching_pools_status", "matching_pools", ["status"])
    op.create_index("idx_matching_pools_member_count", "matching_pools", ["member_count"])
    op.create_index("idx_matching_pools_gender", "matching_pools", ["gender"])
    op.create_index("idx_matching_pools_creator", "matching_pools", ["creator_id"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_matching_pools_creator", table_name="matching_pools")
    op.drop_index("idx_matching_pools_gender", table_name="matching_pools")
    op.drop_index("idx_matching_pools_member_count", table_name="matching_pools")
    op.drop_index("idx_matching_pools_status", table_name="matching_pools")

    # Drop table
    op.drop_table("matching_pools")

