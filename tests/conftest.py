from __future__ import annotations

import sys
from pathlib import Path
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

REPO_ROOT = Path(__file__).resolve().parents[1]

def ensure_repo_root_on_path() -> None:
    """Ensure repository-local packages are importable during pytest collection."""
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

ensure_repo_root_on_path()

from app.core.database import AsyncSessionFactory, create_all_tables, drop_all_tables, engine

@pytest_asyncio.fixture(scope="session")
async def test_db_setup():
    """Create database tables only for tests that request database access."""
    await create_all_tables()
    yield
    await drop_all_tables()


@pytest_asyncio.fixture
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh async database session for each test."""
    async with AsyncSessionFactory() as session:
        yield session
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.create_all)
            pass
        await session.rollback()
        await session.close()
