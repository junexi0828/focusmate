"""add_post_read_table

Revision ID: 20251212_2000
Revises: 20251212_1852
Create Date: 2025-12-12 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251212_2000'
down_revision: Union[str, None] = 'c7c2df775040'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create post_read table
    op.create_table(
        'post_read',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('post_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_read_post_id'), 'post_read', ['post_id'], unique=False)
    op.create_index(op.f('ix_post_read_user_id'), 'post_read', ['user_id'], unique=False)
    # Create unique constraint for (post_id, user_id) to prevent duplicates
    op.create_index('ix_post_read_post_user', 'post_read', ['post_id', 'user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_post_read_post_user', table_name='post_read')
    op.drop_index(op.f('ix_post_read_user_id'), table_name='post_read')
    op.drop_index(op.f('ix_post_read_post_id'), table_name='post_read')
    op.drop_table('post_read')

