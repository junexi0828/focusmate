"""Pytest configuration and fixtures."""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.infrastructure.database.base import Base
from app.core.config import settings


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/focusmate_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "id": "test_user_123",
        "email": "test@example.com",
        "role": "user",
    }


@pytest.fixture
def test_admin():
    """Test admin user data."""
    return {
        "id": "admin_user_123",
        "email": "admin@example.com",
        "role": "admin",
    }


@pytest.fixture
def test_super_admin():
    """Test super admin user data."""
    return {
        "id": "super_admin_123",
        "email": "superadmin@example.com",
        "role": "super_admin",
    }
