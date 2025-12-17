"""Add room reservation recurrence and notification fields

Revision ID: 20251218_0001
Revises: 20251212_1851
Create Date: 2025-12-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251218_0001'
down_revision: Union[str, None] = '20251212_1851'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add recurrence_type column
    op.add_column('room_reservations', sa.Column('recurrence_type', sa.String(length=20), nullable=True, server_default='none', comment='Recurrence pattern: none, daily, weekly, monthly'))

    # Add recurrence_end_date column
    op.add_column('room_reservations', sa.Column('recurrence_end_date', sa.DateTime(timezone=True), nullable=True, comment='When to stop creating recurring reservations'))

    # Add notification_minutes column
    op.add_column('room_reservations', sa.Column('notification_minutes', sa.Integer(), nullable=False, server_default='5', comment='Minutes before scheduled time to send notification'))

    # Add notification_sent column
    op.add_column('room_reservations', sa.Column('notification_sent', sa.Boolean(), nullable=False, server_default='false', comment='Whether notification has been sent'))


def downgrade() -> None:
    op.drop_column('room_reservations', 'notification_sent')
    op.drop_column('room_reservations', 'notification_minutes')
    op.drop_column('room_reservations', 'recurrence_end_date')
    op.drop_column('room_reservations', 'recurrence_type')
