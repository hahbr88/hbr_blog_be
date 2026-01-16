"""add upload thumbnails

Revision ID: 3b1b5b7f51d2
Revises: 9e3c0b1f3a1b
Create Date: 2026-01-16 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3b1b5b7f51d2"
down_revision: Union[str, Sequence[str], None] = "9e3c0b1f3a1b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("uploads", sa.Column("thumbnail_key", sa.String(length=512), nullable=True))
    op.add_column("uploads", sa.Column("thumbnail_url", sa.String(length=1024), nullable=True))
    op.add_column(
        "uploads", sa.Column("thumbnail_content_type", sa.String(length=255), nullable=True)
    )
    op.add_column("uploads", sa.Column("thumbnail_size", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("uploads", "thumbnail_size")
    op.drop_column("uploads", "thumbnail_content_type")
    op.drop_column("uploads", "thumbnail_url")
    op.drop_column("uploads", "thumbnail_key")
