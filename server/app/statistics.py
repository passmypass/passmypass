"""
Statistics tracking module for privacy-preserving aggregate metrics.

All statistics are stored as daily aggregates only - no individual user data.
"""
import logging
from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger("passmypass")


async def increment_stat(db: AsyncSession, **increments: int) -> None:
    """
    Atomically increment one or more statistics for today.
    Uses PostgreSQL UPSERT (INSERT ... ON CONFLICT UPDATE) for atomic operation.
    """
    if not increments:
        return

    today = date.today()

    # Build the SET clause for the upsert
    columns = list(increments.keys())
    values_placeholders = ", ".join(f":val_{col}" for col in columns)
    update_clause = ", ".join(
        f"{col} = daily_statistics.{col} + EXCLUDED.{col}" for col in columns
    )

    query = text(f"""
        INSERT INTO daily_statistics (date, {", ".join(columns)})
        VALUES (:today, {values_placeholders})
        ON CONFLICT (date) DO UPDATE SET
            {update_clause}
    """)

    params = {"today": today}
    for col in columns:
        params[f"val_{col}"] = increments[col]

    await db.execute(query, params)


async def track_secret_creation(
    db: AsyncSession,
    is_file: bool,
    ttl_seconds: int,
    size_bytes: int,
    is_password_protected: bool,
) -> None:
    """Track a secret creation event."""
    increments = {
        "secrets_created": 1,
        "total_ttl_seconds": ttl_seconds,
        "total_size_bytes": size_bytes,
    }

    if is_file:
        increments["files_created"] = 1

    if is_password_protected:
        increments["password_protected_count"] = 1

    await increment_stat(db, **increments)


async def track_secret_claim(db: AsyncSession, created_at: datetime) -> None:
    """Track a successful secret claim."""
    now = datetime.now(timezone.utc)
    time_to_claim = int((now - created_at).total_seconds())

    await increment_stat(
        db,
        secrets_claimed=1,
        total_time_to_claim_seconds=max(0, time_to_claim),
    )


async def track_failed_claim(db: AsyncSession, reason: str) -> None:
    """
    Track a failed claim attempt.
    reason: "invalid" | "expired" | "consumed"
    """
    column_map = {
        "invalid": "failed_claims_invalid",
        "expired": "failed_claims_expired",
        "consumed": "failed_claims_consumed",
    }

    column = column_map.get(reason)
    if column:
        await increment_stat(db, **{column: 1})
    else:
        logger.warning(f"Unknown failed claim reason: {reason}")


async def track_expired_unclaimed(db: AsyncSession, count: int) -> None:
    """Track secrets that expired without being claimed."""
    if count > 0:
        await increment_stat(db, expired_unclaimed=count)


async def track_validation_error(db: AsyncSession) -> None:
    """Track a validation error."""
    await increment_stat(db, validation_errors=1)


async def track_chat_room_creation(db: AsyncSession) -> None:
    """Track a chat room creation event."""
    await increment_stat(db, chat_rooms_created=1)


async def track_chat_message_relayed(db: AsyncSession) -> None:
    """Track a chat message relayed through the server."""
    await increment_stat(db, chat_messages_relayed=1)


async def track_rate_limit_hit(db: AsyncSession) -> None:
    """Track a rate limit hit."""
    await increment_stat(db, rate_limit_hits=1)
