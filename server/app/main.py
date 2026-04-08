import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from app.database import async_session
from app.routes import router, limiter
from app.chat import router as chat_router, cleanup_expired_rooms
from app.config import get_settings
from app import statistics

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("passmypass")

# Cleanup task references
cleanup_task: asyncio.Task | None = None
chat_cleanup_task: asyncio.Task | None = None


async def cleanup_expired_secrets():
    """Background task to remove expired and consumed secrets."""
    while True:
        try:
            async with async_session() as db:
                # First, count expired unclaimed secrets for statistics
                expired_unclaimed_result = await db.execute(
                    text("""
                        SELECT COUNT(*) FROM one_time_secrets
                        WHERE expires_at <= NOW()
                          AND consumed_at IS NULL
                    """)
                )
                expired_unclaimed_count = expired_unclaimed_result.scalar() or 0

                # Track expired unclaimed secrets
                if expired_unclaimed_count > 0:
                    await statistics.track_expired_unclaimed(db, expired_unclaimed_count)
                    await db.commit()

                # Now delete all expired and consumed secrets
                result = await db.execute(
                    text("""
                        DELETE FROM one_time_secrets
                        WHERE expires_at <= NOW()
                           OR consumed_at IS NOT NULL
                    """)
                )
                await db.commit()
                deleted = result.rowcount
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} expired/consumed secrets")
        except Exception as e:
            logger.error(f"Cleanup task error: {type(e).__name__}")

        await asyncio.sleep(settings.cleanup_interval_seconds)


def _run_alembic_upgrade():
    """Run alembic upgrade (called in thread pool to avoid event loop conflicts)."""
    from alembic.config import Config
    from alembic import command
    import os

    # Get the path to alembic.ini relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_ini = os.path.join(base_dir, "alembic.ini")

    alembic_cfg = Config(alembic_ini)
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))

    # Override database URL from settings if needed
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    command.upgrade(alembic_cfg, "head")


async def run_alembic_migrations():
    """Run alembic migrations in a thread pool to avoid event loop conflicts."""
    import concurrent.futures

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, _run_alembic_upgrade)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    global cleanup_task, chat_cleanup_task

    # Run alembic migrations on startup (in thread pool)
    await run_alembic_migrations()
    logger.info("Database migrations applied")

    # Start cleanup tasks
    cleanup_task = asyncio.create_task(cleanup_expired_secrets())
    chat_cleanup_task = asyncio.create_task(cleanup_expired_rooms())
    logger.info("Cleanup schedulers started")

    yield

    # Cancel cleanup tasks on shutdown
    for task in [cleanup_task, chat_cleanup_task]:
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    logger.info("Application shutdown complete")


app = FastAPI(
    title="PassMyPass API",
    description="Secure one-time secret sharing API with zero-knowledge encryption. "
    "All encryption happens client-side — the server never sees plaintext.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add rate limiting
app.state.limiter = limiter


async def rate_limit_handler_with_stats(request: Request, exc: RateLimitExceeded):
    """Custom rate limit handler that tracks statistics."""
    try:
        async with async_session() as db:
            await statistics.track_rate_limit_hit(db)
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to track rate limit stat: {type(e).__name__}")

    # Return the standard rate limit response
    return _rate_limit_exceeded_handler(request, exc)


app.add_exception_handler(RateLimitExceeded, rate_limit_handler_with_stats)


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with logging and user-friendly response."""
    # Generate unique error ID for tracking
    error_id = str(uuid.uuid4())[:8]

    # Log error details (no sensitive data - only method, path, error type)
    logger.error(
        f"Unexpected error [{error_id}]: {type(exc).__name__} | "
        f"Method: {request.method} | Path: {request.url.path}"
    )

    # Return user-friendly error response
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Something went wrong. Please try again later.",
            "error_id": error_id,
        },
    )


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)

    # Mandatory security headers per spec
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self' wss: ws:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # Apply strict no-cache only to API routes (secrets, chat) to prevent caching sensitive data.
    # Non-API routes (health check, etc.) can use default caching behavior.
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"

    return response


# CORS - required for cross-origin requests from frontend
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )


# Include routes
app.include_router(router)
app.include_router(chat_router)


# Health check endpoint (no rate limit)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
