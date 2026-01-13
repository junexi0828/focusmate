"""Database session management.

This module provides SQLAlchemy async session management.
Supports both SQLite (development) and PostgreSQL (production).
"""

from typing import Annotated
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


# Create async engine with database-specific configuration
engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
}

def _using_pgbouncer(database_url: str) -> bool:
    """Detect pgBouncer-style connection URLs.

    Supabase uses pgBouncer on port 6543 in transaction mode, which is not
    compatible with asyncpg prepared statements.
    """
    try:
        parsed_url = make_url(database_url)
    except Exception:
        return False

    if parsed_url.port == 6543:
        return True

    # Allow explicit opt-in via query param (?pgbouncer=true)
    return str(parsed_url.query.get("pgbouncer", "")).lower() in {"1", "true", "yes"}


def _get_connect_args(database_url: str) -> dict:
    """Build connect args, disabling statement cache when pgBouncer is detected."""
    import logging

    logger = logging.getLogger(__name__)

    # Never let detection override an explicit env flag
    env_flag = bool(settings.DATABASE_PGBOUNCER)
    auto_detected = _using_pgbouncer(database_url)
    is_pgbouncer = env_flag or auto_detected

    logger.info(
        "PgBouncer detection: env_flag=%s auto_detected=%s using=%s",
        env_flag,
        auto_detected,
        is_pgbouncer,
    )

    if is_pgbouncer:
        # pgBouncer transaction/statement pool mode cannot handle prepared statements
        return {"statement_cache_size": 0}

    return {}


# Only add pool settings for PostgreSQL (SQLite doesn't support pooling)
if settings.DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
        }
    )

    # Merge connect_args so nothing else overwrites our statement_cache_size
    connect_args = dict(engine_kwargs.get("connect_args", {}))
    connect_args.update(_get_connect_args(settings.DATABASE_URL))
    if connect_args:
        engine_kwargs["connect_args"] = connect_args

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
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
        except Exception:
            await session.rollback()
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
