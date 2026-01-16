"""create uploads table

Revision ID: 9e3c0b1f3a1b
Revises: de6fd484e0f5
Create Date: 2026-01-16 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9e3c0b1f3a1b"
down_revision: Union[str, Sequence[str], None] = "de6fd484e0f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "uploads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("content_type", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(op.f("ix_uploads_id"), "uploads", ["id"], unique=False)
    op.create_index(op.f("ix_uploads_key"), "uploads", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_uploads_key"), table_name="uploads")
    op.drop_index(op.f("ix_uploads_id"), table_name="uploads")
    op.drop_table("uploads")
