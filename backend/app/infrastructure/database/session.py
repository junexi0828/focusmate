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

# Global engine and session variables (initialized lazily to avoid uvicorn worker hangs)
_engine: AsyncEngine | None = None
_AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None
_engine_lock: asyncio.Lock | None = None
logger = logging.getLogger(__name__)

def _using_pgbouncer(database_url: str) -> bool:
    """Detect pgBouncer-style connection URLs."""
    try:
        parsed_url = make_url(database_url)
    except Exception:
        return False

    if parsed_url.port in {6432, 6543}:
        return True

    hostname = (parsed_url.host or "").lower()
    if any(token in hostname for token in ("pooler", "pgbouncer")):
        return True

    if str(parsed_url.query.get("pgbouncer", "")).lower() in {"1", "true", "yes"}:
        return True

    pool_mode = str(parsed_url.query.get("pool_mode", "")).lower()
    return pool_mode in {"transaction", "statement"}


def _get_connect_args(database_url: str) -> tuple[dict, dict, bool, bool]:
    """Build connect args/engine args, disabling prepared statements for pgBouncer."""
    env_flag = bool(settings.DATABASE_PGBOUNCER)
    auto_detected = _using_pgbouncer(database_url)

    url_lower = database_url.lower()
    hostname_detected = ".pooler." in url_lower or "pgbouncer" in url_lower

    try:
        parsed_url = make_url(database_url)
        query = {key.lower(): str(value).lower() for key, value in parsed_url.query.items()}
    except Exception:
        query = {}

    query_disables_prepared = any(
        query.get(key) in {"0", "false", "no"}
        for key in ("statement_cache_size", "max_cached_statement_lifetime", "max_cacheable_statement_size")
    )

    is_pgbouncer = env_flag or auto_detected or hostname_detected
    is_production = settings.APP_ENV in {"production", "staging"}

    # Fundamental decision: Disable prepared stays if it's pgbouncer or production (for safety)
    disable_prepared = is_pgbouncer or is_production or query_disables_prepared or settings.DATABASE_DISABLE_PREPARED_STATEMENTS

    if disable_prepared:
        connect_args = {
            "statement_cache_size": 0,
            "max_cached_statement_lifetime": 0,
            "max_cacheable_statement_size": 0,
        }
        engine_args = {} # prepared_statement_cache_size=0 causes TypeError with NullPool in some setups
        return connect_args, engine_args, True, True

    return {}, {}, False, False


async def _get_engine_and_session() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Lazy initialization of database engine and session factory to prevent process hangs."""
    global _engine, _AsyncSessionLocal

    if _engine and _AsyncSessionLocal:
        return _engine, _AsyncSessionLocal

    async with _engine_lock:
        if _engine and _AsyncSessionLocal:
            return _engine, _AsyncSessionLocal

        db_url = settings.DATABASE_URL
        kw = {"echo": settings.DATABASE_ECHO}

        connect_args, engine_args, use_null_pool, disable_prepared = _get_connect_args(db_url)
        kw.update(engine_args)

        if disable_prepared:
            ca = dict(kw.get("connect_args", {}))
            ca.update(connect_args)
            kw["connect_args"] = ca
            kw["poolclass"] = NullPool
            # Clean up pooling arguments that are incompatible with NullPool
            for key in ("pool_size", "max_overflow", "pool_timeout", "pool_recycle", "pool_use_lifo"):
                kw.pop(key, None)
        else:
            kw.update({
                "pool_pre_ping": True,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
                "pool_recycle": settings.DATABASE_POOL_RECYCLE,
                "pool_use_lifo": settings.DATABASE_POOL_USE_LIFO,
            })

        _engine = create_async_engine(db_url, **kw)
        _AsyncSessionLocal = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        return _engine, _AsyncSessionLocal


def is_duplicate_prepared_statement_error(exc: BaseException) -> bool:
    """Detect asyncpg prepared statement collisions."""
    orig = getattr(exc, "orig", None)
    if orig and orig.__class__.__name__ == "DuplicatePreparedStatementError":
        return True
    return "DuplicatePreparedStatementError" in str(exc)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session with lazy initialization."""
    _, session_factory = await _get_engine_and_session()

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            if is_duplicate_prepared_statement_error(exc):
                # Handle error by resetting engine
                global _engine, _AsyncSessionLocal
                async with _engine_lock:
                    if _engine:
                        await _engine.dispose()
                    _engine = None
                    _AsyncSessionLocal = None
            raise
        finally:
            await session.close()

# Type alias for dependency injection
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

async def reset_engine_for_prepared_statement_error():
    """Reset the database engine to recover from prepared statement errors."""
    global _engine, _AsyncSessionLocal
    async with _engine_lock:
        if _engine:
            await _engine.dispose()
        _engine = None
        _AsyncSessionLocal = None
        logger.warning("♻️ Database engine reset due to prepared statement error")

async def init_db() -> None:
    """Initialize database (create tables)."""
    engine, _ = await _get_engine_and_session()
    from app.infrastructure.database.base import Base
    import app.infrastructure.database.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    """Close database connections."""
    global _engine
    if _engine:
        await _engine.dispose()
