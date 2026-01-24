"""Database session management.

This module provides SQLAlchemy async session management.
Supports both SQLite (development) and PostgreSQL (production).
"""

from typing import Annotated
from collections.abc import AsyncGenerator

import asyncio
import logging

from fastapi import Depends
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, Pool
from sqlalchemy import event

from app.core.config import settings


# Create async engine with database-specific configuration
engine_kwargs = {"echo": settings.DATABASE_ECHO}
logger = logging.getLogger(__name__)
_engine_reset_lock = asyncio.Lock()

def _using_pgbouncer(database_url: str) -> bool:
    """Detect pgBouncer-style connection URLs.

    Supabase and similar providers use pgBouncer in transaction mode, which is
    not compatible with asyncpg prepared statements.
    """
    try:
        parsed_url = make_url(database_url)
    except Exception:
        return False

    if parsed_url.port in {6432, 6543}:
        return True

    hostname = (parsed_url.host or "").lower()
    if any(token in hostname for token in ("pooler", "pgbouncer")):
        return True

    # Allow explicit opt-in via query param (?pgbouncer=true)
    if str(parsed_url.query.get("pgbouncer", "")).lower() in {"1", "true", "yes"}:
        return True

    pool_mode = str(parsed_url.query.get("pool_mode", "")).lower()
    return pool_mode in {"transaction", "statement"}


def _get_connect_args(database_url: str) -> tuple[dict, dict, bool, bool]:
    """Build connect args/engine args for psycopg3 driver.

    psycopg3 is natively compatible with PgBouncer Transaction Mode.
    We only need to set prepare_threshold=None to disable prepared statements.
    Note: prepare_threshold=0 means "prepare all queries immediately" (wrong!)

    Returns (connect_args, engine_args, use_null_pool, disable_prepared).
    """
    # Never let detection override an explicit env flag
    env_flag = bool(settings.DATABASE_PGBOUNCER)
    auto_detected = _using_pgbouncer(database_url)

    # Extra check: Supabase pooler hostnames often contain ".pooler."
    url_lower = database_url.lower()
    hostname_detected = ".pooler." in url_lower or "pgbouncer" in url_lower

    try:
        parsed_url = make_url(database_url)
    except Exception:
        parsed_url = None

    is_pgbouncer = env_flag or auto_detected or hostname_detected
    parsed_host = ((parsed_url.host if parsed_url else None) or "").lower()
    is_local_host = parsed_host in {"localhost", "127.0.0.1", "::1"}

    # If APP_ENV is misconfigured, favor safety for non-local DB hosts.
    force_disable_prepared = settings.APP_ENV in {"production", "staging"}
    remote_host_default = not is_local_host
    disable_prepared = (
        settings.DATABASE_DISABLE_PREPARED_STATEMENTS
        or is_pgbouncer
        or force_disable_prepared
        or remote_host_default
    )

    logger.info(
        "PgBouncer detection: env_flag=%s auto_detected=%s hostname_detected=%s using=%s remote_host_default=%s disable_prepared=%s",
        env_flag,
        auto_detected,
        hostname_detected,
        is_pgbouncer,
        remote_host_default,
        disable_prepared,
    )

    if disable_prepared:
        # psycopg3 uses prepare_threshold to control prepared statements
        # prepare_threshold=None disables prepared statements completely
        # prepare_threshold=0 would prepare ALL queries (wrong for PgBouncer!)
        # This is safe for PgBouncer Transaction Mode
        connect_args = {
            "prepare_threshold": None,  # Disable prepared statements for PgBouncer
        }
        logger.info("Disabling prepared statements for PgBouncer (psycopg3: prepare_threshold=None)")
        return connect_args, {}, is_pgbouncer, True

    return {}, {}, False, False


def is_duplicate_prepared_statement_error(exc: BaseException) -> bool:
    """Detect asyncpg prepared statement collisions (pgBouncer transaction pool)."""
    orig = getattr(exc, "orig", None)
    if orig:
        orig_name = orig.__class__.__name__
        if orig_name in {"DuplicatePreparedStatementError", "DuplicatePreparedStatement"}:
            return True
    error_text = str(exc)
    return (
        "DuplicatePreparedStatementError" in error_text
        or "DuplicatePreparedStatement" in error_text
        or ("prepared statement" in error_text.lower() and "already exists" in error_text.lower())
    )


def _force_disable_prepared_statements(
    database_url: str, engine_kwargs: dict
) -> tuple[str, dict]:
    """Force-disable prepared statements for psycopg3 driver.

    This is used as a last resort when DuplicatePreparedStatementError occurs.
    With psycopg3, this should rarely happen as it handles PgBouncer well.
    """
    if not database_url.startswith("postgresql"):
        return database_url, engine_kwargs

    # Ensure connect_args has the correct psycopg3 parameter
    connect_args = dict(engine_kwargs.get("connect_args", {}))
    connect_args["prepare_threshold"] = None  # psycopg3: disable prepared statements

    engine_kwargs["connect_args"] = connect_args

    logger.warning(
        "Force-disabling prepared statements (psycopg3: prepare_threshold=None). "
        "This should not happen if initial detection worked correctly."
    )

    return database_url, engine_kwargs


async def reset_engine_for_prepared_statement_error() -> None:
    """Recreate the engine with prepared statements and pooling disabled."""
    async with _engine_reset_lock:
        global engine, AsyncSessionLocal, engine_kwargs, database_url
        await engine.dispose()
        reset_kwargs = dict(engine_kwargs)
        reset_url, reset_kwargs = _force_disable_prepared_statements(
            database_url, reset_kwargs
        )
        engine_kwargs = reset_kwargs
        database_url = reset_url
        engine = create_async_engine(
            database_url,
            **engine_kwargs,
        )
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )


# Only add pool settings for PostgreSQL (SQLite doesn't support pooling)
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql"):
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
            "pool_recycle": settings.DATABASE_POOL_RECYCLE,
            "pool_use_lifo": settings.DATABASE_POOL_USE_LIFO,
        }
    )

    # Get PgBouncer-specific settings for psycopg3
    connect_args = dict(engine_kwargs.get("connect_args", {}))
    (
        pgbouncer_connect_args,
        pgbouncer_engine_args,
        use_null_pool,
        disable_prepared,
    ) = _get_connect_args(database_url)

    # Apply PgBouncer-safe connect_args (psycopg3: prepare_threshold=None)
    connect_args.update(pgbouncer_connect_args)

    # Always set connect_args
    engine_kwargs["connect_args"] = connect_args

    # Apply any additional engine args
    engine_kwargs.update(pgbouncer_engine_args)

    # NOTE: With psycopg3, NullPool is optional for PgBouncer
    # psycopg3 handles prepared statements smartly, so normal pooling works fine
    # However, we keep NullPool option for maximum safety in transaction mode
    if use_null_pool:
        # Remove pool-related kwargs as they're incompatible with NullPool
        engine_kwargs.pop("pool_pre_ping", None)
        engine_kwargs.pop("pool_size", None)
        engine_kwargs.pop("max_overflow", None)
        engine_kwargs.pop("pool_timeout", None)
        engine_kwargs.pop("pool_recycle", None)
        engine_kwargs.pop("pool_use_lifo", None)

        # Set NullPool
        engine_kwargs["poolclass"] = NullPool
        logger.warning(
            "Using NullPool for PgBouncer Transaction Mode (psycopg3). "
            "Connection pooling is handled by PgBouncer."
        )

    # Log final config (sanitized URL)
    try:
        parsed_url = make_url(database_url)
        sanitized_url = parsed_url._replace(password="***")
    except Exception:
        sanitized_url = "unparseable"

    connect_args_info = engine_kwargs.get("connect_args", {})
    logger.info(
        "DB engine init (psycopg3): url=%s prepare_threshold=%s pool_size=%s max_overflow=%s pool_timeout=%s disable_prepared=%s",
        sanitized_url,
        connect_args_info.get("prepare_threshold", "default"),
        engine_kwargs.get("pool_size"),
        engine_kwargs.get("max_overflow"),
        engine_kwargs.get("pool_timeout"),
        disable_prepared,
    )

engine: AsyncEngine = create_async_engine(
    database_url,
    **engine_kwargs,
).execution_options(
    # Disable prepared statements at engine level for PgBouncer compatibility
    # This ensures all queries (including SQLAlchemy internal queries) don't use prepared statements
    compiled_cache=None,  # Disable statement caching
)

# CRITICAL FIX: Ensure prepared statements are disabled for EVERY connection
# Register event on Pool before any connections are created
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Disable prepared statements for each new connection.

    This ensures prepared statements are disabled even for internal SQLAlchemy queries.
    Required for PgBouncer Transaction Mode compatibility.
    """
    # For psycopg3, set prepare_threshold to None on the connection object
    if hasattr(dbapi_conn, 'prepare_threshold'):
        dbapi_conn.prepare_threshold = None
        logger.info("Pool connect event: Set prepare_threshold=None on connection")
    else:
        logger.info("Pool connect event: Connection established (prepare_threshold not available)")

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            if is_duplicate_prepared_statement_error(exc):
                logger.error(
                    "Duplicate prepared statement error detected; disposing engine to reset connections.",
                    exc_info=True,
                )
                await reset_engine_for_prepared_statement_error()
            raise
        finally:
            await session.close()


# Type alias for dependency injection
# This is FastAPI's recommended pattern: Annotated[AsyncSession, Depends(get_db)]
# FastAPI will extract the Depends() at runtime, leaving AsyncSession as the actual type
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


async def init_db() -> None:
    """Initialize database (create tables).

    Note: In production, use Alembic migrations instead.
    This is only for development/testing.
    """
    from app.infrastructure.database.base import Base

    # Import all models to ensure they're registered with Base.metadata
    import app.infrastructure.database.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections.

    Should be called on application shutdown.
    """
    await engine.dispose()
