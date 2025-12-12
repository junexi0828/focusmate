"""add is_admin field to user table

Revision ID: ded7a0d90afe
Revises: 97fc315f3aeb
Create Date: 2025-12-12 06:43:54.338262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ded7a0d90afe'
down_revision: Union[str, None] = '97fc315f3aeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_admin column to user table with default value False
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false', comment='Admin user status'))


def downgrade() -> None:
    # Remove is_admin column from user table
    op.drop_column('user', 'is_admin')
