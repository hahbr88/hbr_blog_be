"""set default false for posts.is_temp

Revision ID: de6fd484e0f5
Revises: 63c6fdcede02
Create Date: 2026-01-16 02:27:11.136563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de6fd484e0f5'
down_revision: Union[str, Sequence[str], None] = '63c6fdcede02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("posts", "is_temp", server_default=sa.text("false"))

def downgrade():
    op.alter_column("posts", "is_temp", server_default=None)