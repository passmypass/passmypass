"""add_daily_statistics

Revision ID: 002
Revises: 001
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Create the daily_statistics table for aggregate metrics."""
    if table_exists("daily_statistics"):
        return

    op.create_table(
        "daily_statistics",
        sa.Column("date", sa.Date(), nullable=False),
        # Creation metrics
        sa.Column("secrets_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("files_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_ttl_seconds", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("total_size_bytes", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("password_protected_count", sa.Integer(), server_default="0", nullable=False),
        # Retrieval metrics
        sa.Column("secrets_claimed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_time_to_claim_seconds", sa.BigInteger(), server_default="0", nullable=False),
        # Expiration/failure metrics
        sa.Column("expired_unclaimed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_claims_invalid", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_claims_expired", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_claims_consumed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("validation_errors", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rate_limit_hits", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("date"),
    )


def downgrade() -> None:
    """Drop the daily_statistics table."""
    op.drop_table("daily_statistics")
