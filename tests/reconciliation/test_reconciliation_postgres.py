from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

pytestmark = pytest.mark.skipif(
    not os.getenv("RECONCILIATION_TEST_DATABASE_URL"),
    reason="RECONCILIATION_TEST_DATABASE_URL is required",
)


@pytest.mark.asyncio
async def test_reconciliation_schema_and_append_only_trigger():
    engine = create_async_engine(os.environ["RECONCILIATION_TEST_DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            head = await session.scalar(text("SELECT version_num FROM alembic_version"))
            assert head == "20260615_2100_p17_reconcile"
            columns = {
                row[0]
                for row in (
                    await session.execute(
                        text(
                            "SELECT column_name FROM information_schema.columns "
                            "WHERE table_name='curriculum_coverage_snapshots'"
                        )
                    )
                ).all()
            }
            assert "published_total" in columns
            triggers = set(
                (
                    await session.execute(
                        text(
                            "SELECT tgname FROM pg_trigger "
                            "WHERE tgname='trg_answer_key_verification_append_only'"
                        )
                    )
                ).scalars().all()
            )
            assert triggers == {"trg_answer_key_verification_append_only"}
    finally:
        await engine.dispose()
