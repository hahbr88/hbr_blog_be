"""add tags to posts

Revision ID: a1f0d9c2b7e4
Revises: 3b1b5b7f51d2
Create Date: 2026-03-01 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1f0d9c2b7e4"
down_revision: str | Sequence[str] | None = "3b1b5b7f51d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )


def downgrade() -> None:
    op.drop_column("posts", "tags")
