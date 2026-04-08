from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/passmypass"

    # Security settings
    max_payload_size: int = 1 * 1024 * 1024 + 500_000  # ~1.5 MB max (1MB file + encryption overhead)
    max_ttl_seconds: int = 86400  # 24 hours max expiration
    min_ttl_seconds: int = 60  # 1 minute min expiration
    default_ttl_seconds: int = 600  # 10 minutes default

    # Rate limiting
    rate_limit_create: str = "30/minute"
    rate_limit_claim: str = "60/minute"

    # Cleanup
    cleanup_interval_seconds: int = 300  # Run cleanup every 5 minutes

    # CORS - allow frontend to call API from different subdomain
    cors_origins: list[str] = ["https://passmypass.com", "https://www.passmypass.com"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
