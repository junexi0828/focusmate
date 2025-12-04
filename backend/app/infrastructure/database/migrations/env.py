"""Alembic migration environment."""

import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.infrastructure.database.base import Base

# Import all models to ensure they're registered with SQLAlchemy metadata
from app.infrastructure.database.models import (  # noqa: F401
    Achievement,
    Comment,
    CommentLike,
    Conversation,
    Message,
    Participant,
    Post,
    PostLike,
    Room,
    SessionHistory,
    Timer,
    User,
    UserAchievement,
)

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata


def convert_async_url_to_sync(url: str) -> str:
    """Convert async database URL to sync URL for Alembic.

    Alembic uses synchronous SQLAlchemy, so we need to convert:
    - sqlite+aiosqlite:// -> sqlite://
    - postgresql+asyncpg:// -> postgresql://

    Args:
        url: Async database URL

    Returns:
        Synchronous database URL
    """
    # Convert async SQLite URL to sync
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://")

    # Convert async PostgreSQL URL to sync
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://")

    # Already sync URL, return as-is
    return url


# Override sqlalchemy.url from settings (convert async to sync)
sync_url = convert_async_url_to_sync(settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
