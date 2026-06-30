from __future__ import annotations

import pytest
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, MetaData, String, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.diagnostic_transactional_response import (
    DiagnosticTransactionError,
    DiagnosticTransactionInput,
    TransactionalDiagnosticResponseService,
)


pytestmark = pytest.mark.asyncio


metadata = MetaData()

responses = Table = None

responses = __import__("sqlalchemy").Table(
    "diag_tx_responses",
    metadata,
    Column("id", String, primary_key=True),
    Column("learner_id", String, nullable=False),
    Column("session_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("caps_ref", String, nullable=False),
    Column("is_correct", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

mastery = __import__("sqlalchemy").Table(
    "diag_tx_mastery",
    metadata,
    Column("id", String, primary_key=True),
    Column("learner_id", String, nullable=False),
    Column("caps_ref", String, nullable=False),
    Column("theta_delta", Float, nullable=False),
    Column("source_response_id", String, ForeignKey("diag_tx_responses.id"), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

audit_events = __import__("sqlalchemy").Table(
    "diag_tx_audit_events",
    metadata,
    Column("id", String, primary_key=True),
    Column("learner_id", String, nullable=False),
    Column("event_type", String, nullable=False),
    Column("source_response_id", String, ForeignKey("diag_tx_responses.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        yield db

    await engine.dispose()


async def _count(session, table) -> int:
    result = await session.execute(select(func.count()).select_from(table))
    return int(result.scalar_one())


def _service(session) -> TransactionalDiagnosticResponseService:
    return TransactionalDiagnosticResponseService(
        session,
        responses_table=responses,
        mastery_table=mastery,
        audit_events_table=audit_events,
    )


def _input(**overrides) -> DiagnosticTransactionInput:
    data = {
        "learner_id": "learner-1",
        "session_id": "session-1",
        "item_id": "item-1",
        "caps_ref": "math-grade-6-number-sense",
        "is_correct": True,
        "theta_delta": 0.25,
    }
    data.update(overrides)
    return DiagnosticTransactionInput(**data)


async def test_diagnostic_response_success_commits_response_mastery_and_audit(session):
    service = _service(session)

    result = await service.submit_response(_input())

    assert result.learner_id == "learner-1"
    assert await _count(session, responses) == 1
    assert await _count(session, mastery) == 1
    assert await _count(session, audit_events) == 1


@pytest.mark.parametrize(
    "flag",
    ["fail_after_response", "fail_after_mastery", "fail_after_audit"],
)
async def test_diagnostic_response_failure_rolls_back_all_rows(session, flag):
    service = _service(session)

    with pytest.raises(DiagnosticTransactionError):
        await service.submit_response(_input(**{flag: True}))

    assert await _count(session, responses) == 0
    assert await _count(session, mastery) == 0
    assert await _count(session, audit_events) == 0


async def test_diagnostic_response_later_failure_does_not_damage_prior_commit(session):
    service = _service(session)

    await service.submit_response(_input(item_id="item-1"))

    with pytest.raises(DiagnosticTransactionError):
        await service.submit_response(_input(item_id="item-2", fail_after_mastery=True))

    assert await _count(session, responses) == 1
    assert await _count(session, mastery) == 1
    assert await _count(session, audit_events) == 1


async def test_mastery_update_cannot_orphan_a_response(session):
    service = _service(session)

    with pytest.raises(DiagnosticTransactionError):
        await service.submit_response(_input(fail_after_mastery=True))

    assert await _count(session, responses) == 0
    assert await _count(session, mastery) == 0
