"""add_user_verification_tables

Revision ID: 3f0e28052134
Revises: 7082089e3d8f
Create Date: 2025-12-12 13:39:43.961969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f0e28052134'
down_revision: Union[str, None] = '7082089e3d8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_verification table
    op.create_table(
        "user_verification",
        sa.Column("verification_id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True),

        # School information
        sa.Column("school_name", sa.String(100), nullable=False),

        # Department information
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("major_category", sa.String(50), nullable=True),  # 공과대학, 상경계 등

        # Grade information
        sa.Column("grade", sa.String(20), nullable=False),  # 1학년, 2학년, 3학년, 4학년, 대학원
        sa.Column("student_id_encrypted", sa.Text(), nullable=True),  # 암호화된 학번

        # Personal information
        sa.Column("gender", sa.String(10), nullable=False),  # male, female, other

        # Verification information
        sa.Column("verification_status", sa.String(20), nullable=False, server_default="pending"),  # pending, approved, rejected
        sa.Column("submitted_documents", sa.ARRAY(sa.Text()), nullable=True),  # 제출 서류 URL 배열
        sa.Column("admin_note", sa.Text(), nullable=True),

        # Display settings
        sa.Column("badge_visible", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("department_visible", sa.Boolean(), nullable=False, server_default="true"),

        # Timestamps
        sa.Column("submitted_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("verified_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # Create indexes
    op.create_index("idx_user_verification_user_id", "user_verification", ["user_id"])
    op.create_index("idx_user_verification_status", "user_verification", ["verification_status"])
    op.create_index("idx_user_verification_department", "user_verification", ["department"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_user_verification_department", table_name="user_verification")
    op.drop_index("idx_user_verification_status", table_name="user_verification")
    op.drop_index("idx_user_verification_user_id", table_name="user_verification")

    # Drop table
    op.drop_table("user_verification")

