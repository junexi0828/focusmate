"""Add user profile fields and settings

Revision ID: 20251218_profile_settings
Revises: 20251218_add_room_reservation_fields
Create Date: 2025-12-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251218_profile_settings'
down_revision = '20251218_add_room_reservation_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Add school and profile_image columns to user table
    op.add_column('user', sa.Column('school', sa.String(length=100), nullable=True, comment='User school/university'))
    op.add_column('user', sa.Column('profile_image', sa.String(length=500), nullable=True, comment='Profile image URL'))

    # Create user_settings table
    op.create_table(
        'user_settings',
        sa.Column('id', sa.String(length=36), nullable=False, comment='Unique settings identifier (UUID)'),
        sa.Column('user_id', sa.String(length=36), nullable=False, comment='Associated user ID'),
        sa.Column('theme', sa.String(length=20), nullable=False, server_default='system', comment='UI theme (light, dark, system)'),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='ko', comment='Language preference'),
        sa.Column('notification_email', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Email notification enabled'),
        sa.Column('notification_push', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Push notification enabled'),
        sa.Column('notification_session', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Session notification enabled'),
        sa.Column('notification_achievement', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Achievement notification enabled'),
        sa.Column('notification_message', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Message notification enabled'),
        sa.Column('do_not_disturb_start', sa.String(length=5), nullable=True, comment='Do not disturb start time (HH:MM)'),
        sa.Column('do_not_disturb_end', sa.String(length=5), nullable=True, comment='Do not disturb end time (HH:MM)'),
        sa.Column('session_reminder', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Session reminder enabled'),
        sa.Column('custom_settings', sa.JSON(), nullable=True, comment='Additional custom settings'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_settings_user_id'), 'user_settings', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop user_settings table
    op.drop_index(op.f('ix_user_settings_user_id'), table_name='user_settings')
    op.drop_table('user_settings')

    # Remove columns from user table
    op.drop_column('user', 'profile_image')
    op.drop_column('user', 'school')
