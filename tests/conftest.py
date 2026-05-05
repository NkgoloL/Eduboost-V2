from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio
from sqlalchemy import text

from app import models as _models  # noqa: F401
from app.core.database import AsyncSessionLocal, Base, engine


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def _reset_schema() -> None:
    table_names = [table.name for table in reversed(Base.metadata.sorted_tables)]
    async with engine.begin() as conn:
        if table_names:
            joined = ", ".join(table_names)
            await conn.execute(text(f"DROP TABLE IF EXISTS {joined} CASCADE"))
        await conn.run_sync(Base.metadata.create_all)


async def _truncate_all() -> None:
    table_names = [table.name for table in Base.metadata.sorted_tables]
    if not table_names:
        return
    async with engine.begin() as conn:
        joined = ", ".join(table_names)
        await conn.execute(text(f"TRUNCATE TABLE {joined} RESTART IDENTITY CASCADE"))


async def _ensure_audit_rules() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP RULE IF EXISTS audit_events_no_update ON audit_events"))
        await conn.execute(text("DROP RULE IF EXISTS audit_events_no_delete ON audit_events"))
        await conn.execute(
            text(
                "CREATE RULE audit_events_no_update AS "
                "ON UPDATE TO audit_events DO INSTEAD NOTHING"
            )
        )
        await conn.execute(
            text(
                "CREATE RULE audit_events_no_delete AS "
                "ON DELETE TO audit_events DO INSTEAD NOTHING"
            )
        )


@pytest_asyncio.fixture(scope="session")
async def setup_test_schema():
    await _reset_schema()
    await _ensure_audit_rules()
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_test_schema):
    await engine.dispose()
    await _truncate_all()
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()
    await _truncate_all()
