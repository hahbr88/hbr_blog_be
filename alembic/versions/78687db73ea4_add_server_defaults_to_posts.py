"""add server defaults to posts

Revision ID: 78687db73ea4
Revises: 4bf79e6f5e11
Create Date: 2026-01-11 09:10:31.374411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78687db73ea4'
down_revision: Union[str, Sequence[str], None] = '4bf79e6f5e11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("posts", "is_published", server_default=sa.text("false"))
    op.alter_column("posts", "is_deleted", server_default=sa.text("false"))
    op.alter_column("posts", "created_at", server_default=sa.text("now()"))
    op.alter_column("posts", "updated_at", server_default=sa.text("now()"))

def downgrade():
    op.alter_column("posts", "is_published", server_default=None)
    op.alter_column("posts", "is_deleted", server_default=None)
    op.alter_column("posts", "created_at", server_default=None)
    op.alter_column("posts", "updated_at", server_default=None)