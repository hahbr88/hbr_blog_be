"""set default false for is_temp

Revision ID: 63c6fdcede02
Revises: 0a2f18900528
Create Date: 2026-01-16 02:25:17.593006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63c6fdcede02'
down_revision: Union[str, Sequence[str], None] = '0a2f18900528'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("posts", "is_temp", server_default=sa.text("false"))

def downgrade():
    op.alter_column("posts", "is_temp", server_default=None)
