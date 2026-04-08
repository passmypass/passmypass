from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import base64


def validate_base64url(v: str, field_name: str, max_bytes: int | None = None) -> str:
    """Validate that a string is valid base64url and optionally check decoded size."""
    try:
        # Add padding if needed for base64url
        padding = 4 - len(v) % 4
        if padding != 4:
            v_padded = v + "=" * padding
        else:
            v_padded = v
        decoded = base64.urlsafe_b64decode(v_padded)
        if max_bytes and len(decoded) > max_bytes:
            raise ValueError(f"{field_name} exceeds maximum size of {max_bytes} bytes")
        return v
    except Exception as e:
        if "exceeds maximum" in str(e):
            raise
        raise ValueError(f"{field_name} must be valid base64url encoded")


class CreateSecretRequest(BaseModel):
    ciphertext_b64u: str = Field(..., min_length=1)
    nonce_b64u: str = Field(..., min_length=16, max_length=24)  # 12 bytes = 16-24 chars base64
    aad_b64u: str | None = Field(None, max_length=1024)
    claim_hash_b64u: str = Field(..., min_length=43, max_length=44)  # SHA-256 = 32 bytes = 43-44 chars
    expires_in_seconds: int = Field(..., ge=60, le=86400)

    @field_validator("ciphertext_b64u")
    @classmethod
    def validate_ciphertext(cls, v: str) -> str:
        # ~100KB max for text secrets
        return validate_base64url(v, "ciphertext", max_bytes=150_000)

    @field_validator("nonce_b64u")
    @classmethod
    def validate_nonce(cls, v: str) -> str:
        return validate_base64url(v, "nonce", max_bytes=12)

    @field_validator("aad_b64u")
    @classmethod
    def validate_aad(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_base64url(v, "aad", max_bytes=256)

    @field_validator("claim_hash_b64u")
    @classmethod
    def validate_claim_hash(cls, v: str) -> str:
        return validate_base64url(v, "claim_hash", max_bytes=32)


class CreateSecretResponse(BaseModel):
    id: str
    expires_at: datetime


class SecretStatusResponse(BaseModel):
    exists: bool
    consumed: bool
    expired: bool
    expires_at: datetime | None = None


class ClaimSecretRequest(BaseModel):
    claim_token_b64u: str = Field(..., min_length=43)

    @field_validator("claim_token_b64u")
    @classmethod
    def validate_claim_token(cls, v: str) -> str:
        return validate_base64url(v, "claim_token", max_bytes=32)


class ClaimSecretResponse(BaseModel):
    ciphertext_b64u: str
    nonce_b64u: str
    aad_b64u: str | None = None


class ErrorResponse(BaseModel):
    detail: str
