import secrets
import hashlib
import base64
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models import OneTimeSecret
from app.schemas import (
    CreateSecretRequest,
    CreateSecretResponse,
    SecretStatusResponse,
    ClaimSecretRequest,
    ClaimSecretResponse,
)
from app.config import get_settings
from app import statistics

logger = logging.getLogger("passmypass")
router = APIRouter(prefix="/api/secrets", tags=["secrets"])
settings = get_settings()

# Rate limiter - must be the same instance added to app.state in main.py
limiter = Limiter(key_func=get_remote_address)


def decode_base64url(data: str) -> bytes:
    """Decode base64url string to bytes."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def encode_base64url(data: bytes) -> str:
    """Encode bytes to base64url string without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def generate_secret_id() -> str:
    """Generate a cryptographically secure unguessable ID (128+ bits entropy)."""
    return secrets.token_urlsafe(16)  # 128 bits = 22 chars


def hash_claim_token(token: bytes) -> bytes:
    """Hash the claim token with SHA-256."""
    return hashlib.sha256(token).digest()


def get_client_ip_hash(request: Request) -> bytes | None:
    """Extract client IP and hash it for privacy-preserving audit."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else None

    if ip:
        return hashlib.sha256(ip.encode()).digest()
    return None


def hash_user_agent(request: Request) -> bytes | None:
    """Hash the User-Agent header for minimal audit."""
    ua = request.headers.get("User-Agent")
    if ua:
        return hashlib.sha256(ua.encode()).digest()
    return None


@router.post("", response_model=CreateSecretResponse, status_code=201)
@limiter.limit(settings.rate_limit_create)
async def create_secret(
    request: Request,
    body: CreateSecretRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new one-time secret."""
    # Generate unguessable ID
    secret_id = generate_secret_id()

    # Decode base64url inputs
    ciphertext = decode_base64url(body.ciphertext_b64u)
    nonce = decode_base64url(body.nonce_b64u)
    aad = decode_base64url(body.aad_b64u) if body.aad_b64u else None
    claim_hash = decode_base64url(body.claim_hash_b64u)

    # Validate sizes
    if len(ciphertext) > settings.max_payload_size:
        logger.warning(f"Secret creation rejected: payload too large ({len(ciphertext)} bytes)")
        raise HTTPException(status_code=400, detail="Payload too large")

    if len(nonce) != 12:
        logger.warning(f"Secret creation rejected: invalid nonce size ({len(nonce)} bytes)")
        raise HTTPException(status_code=400, detail="Invalid nonce size")

    if len(claim_hash) != 32:
        logger.warning(f"Secret creation rejected: invalid claim hash size ({len(claim_hash)} bytes)")
        raise HTTPException(status_code=400, detail="Invalid claim hash size")

    # Calculate expiration
    ttl = min(max(body.expires_in_seconds, settings.min_ttl_seconds), settings.max_ttl_seconds)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=ttl)

    # Create the secret
    secret = OneTimeSecret(
        id=secret_id,
        ciphertext=ciphertext,
        nonce=nonce,
        aad=aad,
        claim_hash=claim_hash,
        created_at=now,
        expires_at=expires_at,
    )

    db.add(secret)
    await db.commit()

    # Track statistics (password protection is indicated by AAD with salt)
    is_password_protected = aad is not None and len(aad) >= 16
    await statistics.track_secret_creation(
        db,
        is_file=False,
        ttl_seconds=ttl,
        size_bytes=len(ciphertext),
        is_password_protected=is_password_protected,
    )
    await db.commit()

    logger.info(f"Secret created: id={secret_id[:8]}... ttl={ttl}s")
    return CreateSecretResponse(id=secret_id, expires_at=expires_at)


@router.get("/{secret_id}/status", response_model=SecretStatusResponse)
async def get_secret_status(
    secret_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Check if a secret exists and is available (non-consuming)."""
    result = await db.execute(
        select(OneTimeSecret).where(OneTimeSecret.id == secret_id)
    )
    secret = result.scalar_one_or_none()

    if not secret:
        return SecretStatusResponse(exists=False, consumed=False, expired=False)

    now = datetime.now(timezone.utc)
    is_expired = secret.expires_at <= now
    is_consumed = secret.consumed_at is not None

    return SecretStatusResponse(
        exists=True,
        consumed=is_consumed,
        expired=is_expired,
        expires_at=secret.expires_at,
    )


@router.post("/{secret_id}/claim", response_model=ClaimSecretResponse)
@limiter.limit(settings.rate_limit_claim)
async def claim_secret(
    secret_id: str,
    request: Request,
    body: ClaimSecretRequest,
    db: AsyncSession = Depends(get_db),
):
    """Atomically claim and retrieve a one-time secret."""
    # Decode the claim token and compute its hash
    claim_token = decode_base64url(body.claim_token_b64u)
    claim_hash = hash_claim_token(claim_token)

    # Get client info for audit (hashed for privacy)
    ip_hash = get_client_ip_hash(request)
    ua_hash = hash_user_agent(request)

    # Atomic claim using UPDATE ... RETURNING
    # This ensures that even concurrent requests will only succeed once
    result = await db.execute(
        text("""
            UPDATE one_time_secrets
            SET consumed_at = NOW(),
                consumed_by_ip_hash = :ip_hash,
                consumed_ua_hash = :ua_hash
            WHERE id = :id
              AND consumed_at IS NULL
              AND expires_at > NOW()
              AND claim_hash = :claim_hash
            RETURNING ciphertext, nonce, aad, created_at
        """),
        {
            "id": secret_id,
            "claim_hash": claim_hash,
            "ip_hash": ip_hash,
            "ua_hash": ua_hash,
        }
    )
    row = result.fetchone()

    if not row:
        # Determine failure reason for statistics tracking
        check_result = await db.execute(
            select(OneTimeSecret).where(OneTimeSecret.id == secret_id)
        )
        existing = check_result.scalar_one_or_none()

        if existing is None:
            # Invalid ID or wrong claim hash
            await statistics.track_failed_claim(db, "invalid")
        elif existing.consumed_at is not None:
            await statistics.track_failed_claim(db, "consumed")
        elif existing.expires_at <= datetime.now(timezone.utc):
            await statistics.track_failed_claim(db, "expired")
        else:
            # Wrong claim hash
            await statistics.track_failed_claim(db, "invalid")
        await db.commit()

        # Generic error to prevent enumeration
        logger.info(f"Secret claim failed: id={secret_id[:8]}... (not found/expired/consumed)")
        raise HTTPException(
            status_code=404,
            detail="Secret not found or no longer available"
        )

    await db.commit()

    # Track successful claim
    await statistics.track_secret_claim(db, row.created_at)
    await db.commit()

    logger.info(f"Secret claimed: id={secret_id[:8]}...")
    return ClaimSecretResponse(
        ciphertext_b64u=encode_base64url(row.ciphertext),
        nonce_b64u=encode_base64url(row.nonce),
        aad_b64u=encode_base64url(row.aad) if row.aad else None,
    )
