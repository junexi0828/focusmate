"""Add remove_on_leave field to room table

Revision ID: 20251219_0003
Revises: 20251219_0002
Create Date: 2025-12-19 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251219_0003"
down_revision: Union[str, None] = "20251219_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add remove_on_leave column to room table
    op.add_column(
        "room",
        sa.Column(
            "remove_on_leave",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="If true, participants are removed from room when they leave (is_connected=False). If false, participants remain in room list even after leaving.",
        ),
    )


def downgrade() -> None:
    # Remove remove_on_leave column
    op.drop_column("room", "remove_on_leave")
