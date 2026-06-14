"""Disposable-PostgreSQL checks for Phase 1 persistence constraints.

Set PHASE1_TEST_DATABASE_URL to an isolated database whose name contains
"test" and run Alembic to head before executing this module. The tests are
skipped by default so routine unit runs never touch an unknown database.
"""
from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import IntegrityError

from app.models.content_factory import (
    ContentGenerationRun,
    ContentGenerationTask,
    ContentLayer,
    ContentScope,
    ContentValidationReport,
)

DATABASE_URL = os.getenv("PHASE1_TEST_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="PHASE1_TEST_DATABASE_URL is required for disposable PostgreSQL verification",
)


def _guard_test_database() -> None:
    database_name = DATABASE_URL.rsplit("/", 1)[-1].split("?", 1)[0].lower()
    if "test" not in database_name:
        raise RuntimeError("PHASE1_TEST_DATABASE_URL must point to a database containing 'test'")


@pytest.mark.asyncio
async def test_task_only_validation_report_satisfies_database_constraints() -> None:
    _guard_test_database()
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        scope_id = f"phase1-test-{uuid.uuid4()}"
        run_id = uuid.uuid4()
        task_id = uuid.uuid4()
        session.add(
            ContentScope(
                scope_id=scope_id,
                grade=4,
                subject_code="MATHS",
                subject_slug="mathematics",
                subject_display_name="Mathematics",
                language="en",
            )
        )
        await session.flush()
        session.add(ContentGenerationRun(run_id=run_id, scope_id=scope_id, status="created"))
        session.add(
            ContentGenerationTask(
                task_id=task_id,
                run_id=run_id,
                scope_id=scope_id,
                caps_ref="4.M.1.1",
                content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
                status="validation_failed",
            )
        )
        await session.flush()
        session.add(
            ContentValidationReport(
                artifact_id=None,
                task_id=task_id,
                passed=False,
                checks={"source_traceability": False},
                errors=["missing source"],
            )
        )
        await session.flush()
        count = await session.scalar(
            text("SELECT count(*) FROM content_validation_reports WHERE task_id = :task_id"),
            {"task_id": task_id},
        )
        assert count == 1
        await session.close()
        await transaction.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_validation_report_rejects_missing_task_and_artifact() -> None:
    _guard_test_database()
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        session.add(
            ContentValidationReport(
                artifact_id=None,
                task_id=None,
                passed=False,
                checks={},
                errors=["invalid subject"],
            )
        )
        with pytest.raises(IntegrityError):
            await session.flush()
        await session.rollback()
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
    await engine.dispose()
