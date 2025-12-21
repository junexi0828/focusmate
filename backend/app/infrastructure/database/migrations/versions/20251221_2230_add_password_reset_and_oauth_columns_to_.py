"""add_password_reset_and_oauth_columns_to_user

Revision ID: 1b6ce548b5b8
Revises: 20251219_0003
Create Date: 2025-12-21 22:30:37.920568

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b6ce548b5b8"
down_revision: Union[str, None] = "20251219_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password reset columns
    op.add_column(
        "user",
        sa.Column(
            "password_reset_token",
            sa.String(length=255),
            nullable=True,
            comment="Password reset token",
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "password_reset_expires",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Password reset token expiration",
        ),
    )

    # Add OAuth column
    op.add_column(
        "user",
        sa.Column(
            "naver_id",
            sa.String(length=100),
            nullable=True,
            unique=True,
            comment="Naver OAuth ID",
        ),
    )

    # Create indexes
    op.create_index(
        op.f("ix_user_password_reset_token"),
        "user",
        ["password_reset_token"],
        unique=False,
    )
    op.create_index(op.f("ix_user_naver_id"), "user", ["naver_id"], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f("ix_user_naver_id"), table_name="user")
    op.drop_index(op.f("ix_user_password_reset_token"), table_name="user")

    # Drop columns
    op.drop_column("user", "naver_id")
    op.drop_column("user", "password_reset_expires")
    op.drop_column("user", "password_reset_token")
