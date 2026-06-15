import os
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.ai_operations import AIBudgetExceededError, AIOperationsService, BudgetLimits

URL = os.getenv("PHASE6_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="PHASE6_TEST_DATABASE_URL is required")


@pytest.fixture
async def db():
    engine = create_async_engine(URL, pool_pre_ping=True)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_reserve_finalize_is_idempotent_and_updates_counters(db):
    service = AIOperationsService(db, limits=BudgetLimits(1000, 5000, 0.8, 300))
    reservation = await service.reserve(
        operation_id="phase6:test:one",
        user_id="u1",
        tenant_id="t1",
        purpose="learner_tutor",
        estimated_tokens=300,
    )
    again = await service.reserve(
        operation_id="phase6:test:one",
        user_id="u1",
        tenant_id="t1",
        purpose="learner_tutor",
        estimated_tokens=300,
    )
    assert again.reservation_id == reservation.reservation_id
    event = await service.finalize(
        operation_id="phase6:test:one",
        provider="azure_openai",
        model="gpt-4o-mini",
        prompt_tokens=100,
        completion_tokens=50,
    )
    duplicate = await service.finalize(
        operation_id="phase6:test:one",
        provider="azure_openai",
        model="gpt-4o-mini",
        prompt_tokens=100,
        completion_tokens=50,
    )
    assert duplicate.event_id == event.event_id
    summary = await service.counter_view(scope_type="user", scope_id="u1")
    assert summary["used_tokens"] == 150
    assert summary["reserved_tokens"] == 0


@pytest.mark.asyncio
async def test_budget_blocks_concurrent_overspend(db):
    service = AIOperationsService(db, limits=BudgetLimits(500, 1000, 0.8, 300))
    await service.reserve(operation_id="phase6:test:two", user_id="u2", tenant_id="t2", purpose="test", estimated_tokens=400)
    with pytest.raises(AIBudgetExceededError):
        await service.reserve(operation_id="phase6:test:three", user_id="u2", tenant_id="t2", purpose="test", estimated_tokens=200)


@pytest.mark.asyncio
async def test_expiry_releases_reserved_tokens(db):
    service = AIOperationsService(db, limits=BudgetLimits(500, 1000, 0.8, 1))
    old = datetime.now(UTC) - timedelta(minutes=5)
    reservation = await service.reserve(
        operation_id="phase6:test:expired",
        user_id="u3",
        tenant_id="t3",
        purpose="test",
        estimated_tokens=200,
        now=old,
    )
    assert reservation.status == "pending"
    assert await service.expire_stale(now=datetime.now(UTC)) == 1
    summary = await service.counter_view(scope_type="user", scope_id="u3")
    assert summary["reserved_tokens"] == 0


@pytest.mark.asyncio
async def test_usage_events_are_append_only(db):
    service = AIOperationsService(db, limits=BudgetLimits(500, 1000, 0.8, 300))
    await service.reserve(operation_id="phase6:test:immutable", user_id="u4", tenant_id="t4", purpose="test", estimated_tokens=100)
    await service.finalize(operation_id="phase6:test:immutable", provider="groq", model="model", prompt_tokens=10, completion_tokens=10)
    await db.commit()
    with pytest.raises(Exception):
        await db.execute(text("UPDATE ai_usage_events SET provider='tampered' WHERE operation_id='phase6:test:immutable'"))
        await db.commit()
    await db.rollback()
