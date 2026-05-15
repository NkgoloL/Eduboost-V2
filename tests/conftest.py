from __future__ import annotations

import os
import sys
from pathlib import Path
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

REPO_ROOT = Path(__file__).resolve().parents[1]

def ensure_repo_root_on_path() -> None:
    """Ensure repository-local packages are importable during pytest collection."""
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

ensure_repo_root_on_path()
os.environ["APP_ENV"] = "test"
os.environ["ENVIRONMENT"] = "test"

from app.core.database import AsyncSessionFactory, create_all_tables, drop_all_tables, engine


def _require_test_database() -> bool:
    return os.environ.get("EDUBOOST_REQUIRE_TEST_DB", "").lower() in {"1", "true", "yes"}


@pytest_asyncio.fixture(scope="session")
async def test_db_setup():
    """Ensure a clean database schema for tests that request database access."""
    db_url = os.environ.get("DATABASE_URL", "").lower()
    if "prod" in db_url or "staging" in db_url:
        pytest.exit(f"ABORT: DATABASE_URL appears to point to a protected environment ({db_url}). Refusing to run tests and drop tables.")

    try:
        await drop_all_tables()
        await create_all_tables()
    except (OSError, SQLAlchemyError) as exc:
        if _require_test_database():
            raise
        pytest.skip(f"test database is unavailable: {exc}")

    try:
        yield
    finally:
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
