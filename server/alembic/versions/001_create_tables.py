"""create_tables

Revision ID: 001
Revises:
Create Date: 2026-01-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def index_exists(index_name: str) -> bool:
    """Check if an index exists on the one_time_secrets table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = inspector.get_indexes("one_time_secrets")
    return any(idx["name"] == index_name for idx in indexes)


def constraint_exists(constraint_name: str) -> bool:
    """Check if a check constraint exists on the one_time_secrets table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    constraints = inspector.get_check_constraints("one_time_secrets")
    return any(c["name"] == constraint_name for c in constraints)


def upgrade() -> None:
    """Create the one_time_secrets table (idempotent)."""
    # Skip if table already exists (e.g., migrating from pre-alembic setup)
    if table_exists("one_time_secrets"):
        # Table exists, just ensure indexes and constraints are in place
        if not index_exists("idx_one_time_secrets_is_file"):
            op.create_index(
                "idx_one_time_secrets_is_file",
                "one_time_secrets",
                ["is_file"],
                postgresql_where=sa.text("is_file = TRUE"),
            )
        if not constraint_exists("chk_file_has_size"):
            op.create_check_constraint(
                "chk_file_has_size",
                "one_time_secrets",
                "is_file = FALSE OR file_size IS NOT NULL",
            )
        return

    # Create table from scratch
    op.create_table(
        "one_time_secrets",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("nonce", sa.LargeBinary(), nullable=False),
        sa.Column("aad", sa.LargeBinary(), nullable=True),
        sa.Column("claim_hash", sa.LargeBinary(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_by_ip_hash", sa.LargeBinary(), nullable=True),
        sa.Column("consumed_ua_hash", sa.LargeBinary(), nullable=True),
        # File upload support
        sa.Column("is_file", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("encrypted_filename", sa.LargeBinary(), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        "ix_one_time_secrets_expires_at", "one_time_secrets", ["expires_at"]
    )
    op.create_index(
        "ix_one_time_secrets_consumed_at", "one_time_secrets", ["consumed_at"]
    )
    op.create_index(
        "idx_one_time_secrets_is_file",
        "one_time_secrets",
        ["is_file"],
        postgresql_where=sa.text("is_file = TRUE"),
    )

    # Add check constraint for file secrets
    op.create_check_constraint(
        "chk_file_has_size",
        "one_time_secrets",
        "is_file = FALSE OR file_size IS NOT NULL",
    )


def downgrade() -> None:
    """Drop the one_time_secrets table."""
    op.drop_constraint("chk_file_has_size", "one_time_secrets", type_="check")
    op.drop_index("idx_one_time_secrets_is_file", table_name="one_time_secrets")
    op.drop_index("ix_one_time_secrets_consumed_at", table_name="one_time_secrets")
    op.drop_index("ix_one_time_secrets_expires_at", table_name="one_time_secrets")
    op.drop_table("one_time_secrets")
