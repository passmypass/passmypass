from datetime import datetime
from sqlalchemy import Column, Text, LargeBinary, DateTime, Index, Boolean, Integer, String, Date, BigInteger
from app.database import Base


class OneTimeSecret(Base):
    __tablename__ = "one_time_secrets"

    id = Column(Text, primary_key=True)
    ciphertext = Column(LargeBinary, nullable=False)
    nonce = Column(LargeBinary, nullable=False)
    aad = Column(LargeBinary, nullable=True)
    claim_hash = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    consumed_by_ip_hash = Column(LargeBinary, nullable=True)  # SHA-256 hash of IP for privacy
    consumed_ua_hash = Column(LargeBinary, nullable=True)

    # File upload support
    is_file = Column(Boolean, default=False, nullable=False)
    encrypted_filename = Column(LargeBinary, nullable=True)
    content_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)  # Original size in bytes

    __table_args__ = (
        Index("ix_one_time_secrets_expires_at", "expires_at"),
        Index("ix_one_time_secrets_consumed_at", "consumed_at"),
    )


class DailyStatistic(Base):
    """Aggregate daily statistics for privacy-preserving analytics."""
    __tablename__ = "daily_statistics"

    date = Column(Date, primary_key=True)

    # Creation metrics
    secrets_created = Column(Integer, default=0, nullable=False)
    files_created = Column(Integer, default=0, nullable=False)
    total_ttl_seconds = Column(BigInteger, default=0, nullable=False)
    total_size_bytes = Column(BigInteger, default=0, nullable=False)
    password_protected_count = Column(Integer, default=0, nullable=False)

    # Retrieval metrics
    secrets_claimed = Column(Integer, default=0, nullable=False)
    total_time_to_claim_seconds = Column(BigInteger, default=0, nullable=False)

    # Chat room metrics
    chat_rooms_created = Column(Integer, default=0, nullable=False)
    chat_messages_relayed = Column(Integer, default=0, nullable=False)

    # Expiration/failure metrics
    expired_unclaimed = Column(Integer, default=0, nullable=False)
    failed_claims_invalid = Column(Integer, default=0, nullable=False)
    failed_claims_expired = Column(Integer, default=0, nullable=False)
    failed_claims_consumed = Column(Integer, default=0, nullable=False)
    validation_errors = Column(Integer, default=0, nullable=False)
    rate_limit_hits = Column(Integer, default=0, nullable=False)
