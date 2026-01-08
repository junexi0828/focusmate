"""add_refresh_tokens_table

Revision ID: add_refresh_tokens
Revises: 20260105_0009
Create Date: 2026-01-08 12:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_refresh_tokens'
down_revision = '20260105_0009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_id', sa.String(36), nullable=False, unique=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('absolute_expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_rotated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),

        sa.Column('device_info', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Create indexes
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_token_id', 'refresh_tokens', ['token_id'])
    op.create_index('idx_refresh_tokens_family_id', 'refresh_tokens', ['family_id'])


def downgrade() -> None:
    op.drop_index('idx_refresh_tokens_family_id', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_token_id', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
