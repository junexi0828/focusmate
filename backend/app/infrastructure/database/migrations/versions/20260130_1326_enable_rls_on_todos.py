"""Enable RLS on todos

Revision ID: e298b9fb3334
Revises: 88a35ca45f85
Create Date: 2026-01-30 13:26:16.710847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e298b9fb3334'
down_revision: Union[str, None] = '88a35ca45f85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE todos ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY \"Users can only access their own todos\" ON todos FOR ALL USING (auth.uid()::text = user_id)")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS \"Users can only access their own todos\" ON todos")
    op.execute("ALTER TABLE todos DISABLE ROW LEVEL SECURITY")
