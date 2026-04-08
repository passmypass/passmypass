#!/usr/bin/env python3
"""
Create a new Alembic migration with sequential numbering.

Usage:
    python scripts/create_migration.py <migration_name> [--autogenerate]

Examples:
    python scripts/create_migration.py add_user_table
    python scripts/create_migration.py add_index_on_email --autogenerate

Naming convention:
    Migrations are named with a 3-digit sequential prefix: 001_create_tables, 002_add_user_table, etc.
    The script automatically determines the next number based on existing migrations.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_next_revision_number(versions_dir: Path) -> str:
    """Get the next sequential revision number based on existing migrations."""
    existing = []
    for f in versions_dir.glob("*.py"):
        if f.name.startswith("__"):
            continue
        # Extract the numeric prefix (e.g., "001" from "001_create_tables.py")
        parts = f.stem.split("_", 1)
        if parts[0].isdigit():
            existing.append(int(parts[0]))

    next_num = max(existing, default=0) + 1
    return f"{next_num:03d}"


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Alembic migration with sequential numbering"
    )
    parser.add_argument(
        "name",
        help="Migration name (use underscores, e.g., 'add_user_table')",
    )
    parser.add_argument(
        "--autogenerate",
        "-a",
        action="store_true",
        help="Auto-generate migration by comparing models to database",
    )
    args = parser.parse_args()

    # Ensure we're in the server directory
    server_dir = Path(__file__).parent.parent
    os.chdir(server_dir)

    # Get versions directory
    versions_dir = server_dir / "alembic" / "versions"
    if not versions_dir.exists():
        print(f"Error: versions directory not found at {versions_dir}")
        sys.exit(1)

    # Get next revision number
    rev_id = get_next_revision_number(versions_dir)

    # Build alembic command
    cmd = [
        "alembic",
        "revision",
        "--rev-id",
        rev_id,
        "-m",
        args.name,
    ]

    if args.autogenerate:
        cmd.append("--autogenerate")

    print(f"Creating migration: {rev_id}_{args.name}")
    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=server_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
