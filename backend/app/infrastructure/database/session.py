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
from sqlalchemy.pool import NullPool

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
    """Build connect args/engine args, disabling prepared statements for pgBouncer.

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
        query = {key.lower(): str(value).lower() for key, value in parsed_url.query.items()}
    except Exception:
        parsed_url = None
        query = {}

    query_disables_prepared = any(
        query.get(key) in {"0", "false", "no"}
        for key in (
            "statement_cache_size",
            "max_cached_statement_lifetime",
            "max_cacheable_statement_size",
        )
    )

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
        or query_disables_prepared
    )

    logger.info(
        "PgBouncer detection: env_flag=%s auto_detected=%s hostname_detected=%s using=%s remote_host_default=%s query_disables_prepared=%s disable_prepared=%s",
        env_flag,
        auto_detected,
        hostname_detected,
        is_pgbouncer,
        remote_host_default,
        query_disables_prepared,
        disable_prepared,
    )

    if disable_prepared:
        # pgBouncer transaction/statement pool mode cannot handle prepared statements.
        # Production/staging default to disabling to avoid DuplicatePreparedStatementError.
        connect_args = {
            "statement_cache_size": 0,
            "max_cached_statement_lifetime": 0,
            "max_cacheable_statement_size": 0,
        }
        engine_args = {
            # SQLAlchemy asyncpg dialect parameter (not a DBAPI connect arg).
            "prepared_statement_cache_size": 0,
        }
        return connect_args, engine_args, is_pgbouncer, True

    return {}, {}, False, False


def is_duplicate_prepared_statement_error(exc: BaseException) -> bool:
    """Detect asyncpg prepared statement collisions (pgBouncer transaction pool)."""
    orig = getattr(exc, "orig", None)
    if orig and orig.__class__.__name__ == "DuplicatePreparedStatementError":
        return True
    return "DuplicatePreparedStatementError" in str(exc)


def _force_disable_prepared_statements(
    database_url: str, engine_kwargs: dict
) -> tuple[str, dict]:
    """Force-disable asyncpg prepared statements and pooling for pgBouncer safety."""
    if not database_url.startswith("postgresql"):
        return database_url, engine_kwargs

    connect_args = dict(engine_kwargs.get("connect_args", {}))
    connect_args.update(
        {
            "statement_cache_size": 0,
            "max_cached_statement_lifetime": 0,
            "max_cacheable_statement_size": 0,
            # Force asyncpg to disable prepared statements at the protocol level
            "server_settings": {
                "jit": "off",  # Disable JIT to prevent prepared statement usage
            },
        }
    )
    engine_kwargs["connect_args"] = connect_args




    engine_kwargs["poolclass"] = NullPool
    for key in (
        "pool_size",
        "max_overflow",
        "pool_timeout",
        "pool_recycle",
        "pool_use_lifo",
    ):
        engine_kwargs.pop(key, None)

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

    # Merge connect_args so nothing else overwrites our statement_cache_size
    connect_args = dict(engine_kwargs.get("connect_args", {}))
    (
        pgbouncer_connect_args,
        pgbouncer_engine_args,
        use_null_pool,
        disable_prepared,
    ) = _get_connect_args(database_url)
    connect_args.update(pgbouncer_connect_args)
    if connect_args:
        engine_kwargs["connect_args"] = connect_args
    engine_kwargs.update(pgbouncer_engine_args)

    if disable_prepared:
        # Prepared statements are handled via connect_args / engine_kwargs.
        pass

    # pgBouncer already pools connections; using NullPool prevents state leakage and
    # avoids server-side prepared statement collisions in transaction pooling mode.
    if use_null_pool:
        engine_kwargs["poolclass"] = NullPool
        for key in (
            "pool_size",
            "max_overflow",
            "pool_timeout",
            "pool_recycle",
            "pool_use_lifo",
        ):
            engine_kwargs.pop(key, None)

    # Fail-safe: asyncpg prepared statements are unsafe behind pgBouncer transaction pools.
    # Keep them disabled for Postgres when detection or env flags indicate risk.
    if disable_prepared:
        connect_args = dict(engine_kwargs.get("connect_args", {}))
        connect_args.update(
            {
                "statement_cache_size": 0,
                "max_cached_statement_lifetime": 0,
                "max_cacheable_statement_size": 0,
            }
        )
        engine_kwargs["connect_args"] = connect_args
        engine_kwargs["prepared_statement_cache_size"] = 0


    # Log final config (sanitized URL)
    try:
        parsed_url = make_url(database_url)
        sanitized_url = parsed_url._replace(password="***")
    except Exception:
        sanitized_url = "unparseable"

    logger.info(
        "DB engine init: url=%s connect_args=%s poolclass=%s",
        sanitized_url,
        engine_kwargs.get("connect_args"),
        engine_kwargs.get("poolclass").__name__ if engine_kwargs.get("poolclass") else "QueuePool",
    )

engine: AsyncEngine = create_async_engine(
    database_url,
    **engine_kwargs,
)

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
