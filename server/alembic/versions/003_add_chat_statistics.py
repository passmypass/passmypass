"""add_chat_statistics

Revision ID: 003
Revises: 002
Create Date: 2026-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Add chat statistics columns to daily_statistics table."""
    if not column_exists("daily_statistics", "chat_rooms_created"):
        op.add_column(
            "daily_statistics",
            sa.Column("chat_rooms_created", sa.Integer(), server_default="0", nullable=False),
        )

    if not column_exists("daily_statistics", "chat_messages_relayed"):
        op.add_column(
            "daily_statistics",
            sa.Column("chat_messages_relayed", sa.Integer(), server_default="0", nullable=False),
        )


def downgrade() -> None:
    """Remove chat statistics columns from daily_statistics table."""
    op.drop_column("daily_statistics", "chat_messages_relayed")
    op.drop_column("daily_statistics", "chat_rooms_created")
