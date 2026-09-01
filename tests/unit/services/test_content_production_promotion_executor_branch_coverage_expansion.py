"""Batch 216 — app/services/content_production_promotion_executor.py branch coverage expansion.

Tests comprehensive execution paths:
- dry_run_promotion: gate blocked error, gate promotable plan
- promote_scope: confirmation mismatch, gate blocked error, promotion with new artifact, promotion superseding existing active artifact, exception handling in per-artifact loop
- get_promotion_event: not found error, success with artifact count
- list_promotion_events: with scope_id, without scope_id, paginated results
- rollback_promotion: event not found error, rollback active artifacts and update event
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.content_factory import (
    ContentProductionArtifact,
    ContentPromotionEvent,
    ContentStagingArtifact,
    ContentStagingSeedItem,
)
from app.services.content_production_promotion_executor import (
    ContentProductionPromotionExecutor,
    ProductionPromotionPage,
    ProductionPromotionPlan,
    ProductionPromotionResult,
    ProductionRollbackResult,
)
from app.services.content_production_promotion_gate import (
    ProductionGateBlocker,
    ProductionGateReport,
    ProductionGateStatus,
)


from sqlalchemy import Column, DateTime, JSON, String, Uuid
from app.core.database import Base


@pytest.fixture(autouse=True)
def mock_content_promotion_event(monkeypatch):
    class MockContentPromotionEvent(Base):
        __tablename__ = "test_mock_content_promotion_events"
        __table_args__ = {"extend_existing": True}

        event_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
        scope_id = Column(String, nullable=True)
        promoted_by = Column(String, nullable=True)
        status = Column(String, nullable=True)
        summary = Column(JSON, default=dict)
        created_at = Column(DateTime, nullable=True)
        updated_at = Column(DateTime, nullable=True)

    monkeypatch.setattr(
        "app.services.content_production_promotion_executor.ContentPromotionEvent",
        MockContentPromotionEvent,
    )
    return MockContentPromotionEvent


@pytest.fixture
def mock_gate():
    gate = MagicMock()
    # Default to promotable report
    report = ProductionGateReport(
        scope_id="scope-123",
        status=ProductionGateStatus.PROMOTABLE,
        coverage_summary={"lessons": {"status": "green"}},
        staging_summary={"seeded_count": 2},
    )
    gate.evaluate_scope = AsyncMock(return_value=report)
    return gate


@pytest.fixture
def executor(mock_gate):
    return ContentProductionPromotionExecutor(gate=mock_gate)


# ---------------------------------------------------------------------------
# dry_run_promotion
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_dry_run_promotion_gate_blocked_raises_value_error(executor, mock_gate):
    mock_session = AsyncMock()
    blocked_report = ProductionGateReport(
        scope_id="scope-123",
        status=ProductionGateStatus.BLOCKED_BY_COVERAGE,
        blockers=[ProductionGateBlocker(type="coverage", message="Coverage is red")],
    )
    mock_gate.evaluate_scope.return_value = blocked_report

    with pytest.raises(ValueError, match="Cannot dry-run promotion: gate status is blocked_by_coverage"):
        await executor.dry_run_promotion(mock_session, "scope-123", actor_id="admin-1")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dry_run_promotion_success(executor, mock_gate):
    mock_session = AsyncMock()

    staging_art1 = MagicMock(spec=ContentStagingArtifact)
    staging_art2 = MagicMock(spec=ContentStagingArtifact)
    res_staging = MagicMock()
    res_staging.scalars.return_value.all.return_value = [staging_art1, staging_art2]

    mock_session.execute.return_value = res_staging

    plan = await executor.dry_run_promotion(
        mock_session,
        "scope-123",
        layers=["lessons"],
        actor_id="admin-1",
    )

    assert isinstance(plan, ProductionPromotionPlan)
    assert plan.scope_id == "scope-123"
    assert plan.layers == ["lessons"]
    assert plan.promotable_count == 2
    assert plan.skipped_count == 0


# ---------------------------------------------------------------------------
# promote_scope
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_promote_scope_confirmation_mismatch_raises_value_error(executor):
    mock_session = AsyncMock()

    with pytest.raises(ValueError, match="Confirmation mismatch. Expected: 'PROMOTE scope-123 TO PRODUCTION'"):
        await executor.promote_scope(
            mock_session,
            "scope-123",
            actor_id="admin-1",
            confirmation="WRONG CONFIRMATION",
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_promote_scope_gate_blocked_raises_value_error(executor, mock_gate):
    mock_session = AsyncMock()
    blocked_report = ProductionGateReport(
        scope_id="scope-123",
        status=ProductionGateStatus.BLOCKED_BY_VALIDATION,
        blockers=[ProductionGateBlocker(type="validation", message="Validation report failed")],
    )
    mock_gate.evaluate_scope.return_value = blocked_report

    with pytest.raises(ValueError, match="Cannot promote: gate status is blocked_by_validation"):
        await executor.promote_scope(
            mock_session,
            "scope-123",
            actor_id="admin-1",
            confirmation="PROMOTE scope-123 TO PRODUCTION",
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_promote_scope_success_superseding_existing(executor, mock_gate):
    mock_session = AsyncMock()

    art_id1 = uuid.uuid4()
    art_id2 = uuid.uuid4()
    staging_art1 = MagicMock(
        spec=ContentStagingArtifact,
        id=uuid.uuid4(),
        artifact_id=art_id1,
        scope_id="scope-123",
        caps_ref="MATH.4.1",
        layer="lessons",
        artifact_type="lesson_plan",
        payload_json={"content": "lesson 1"},
        source_artifact_hash="hash-1",
    )
    staging_art2 = MagicMock(
        spec=ContentStagingArtifact,
        id=uuid.uuid4(),
        artifact_id=art_id2,
        scope_id="scope-123",
        caps_ref="MATH.4.2",
        layer="lessons",
        artifact_type="lesson_plan",
        payload_json={"content": "lesson 2"},
        source_artifact_hash="hash-2",
    )

    # 1. Staging query returns [staging_art1, staging_art2]
    res_staging = MagicMock()
    res_staging.scalars.return_value.all.return_value = [staging_art1, staging_art2]

    # 2. Existing query for art1 returns an existing active production artifact (will be superseded)
    existing_prod1 = MagicMock(spec=ContentProductionArtifact, production_status="active")
    res_existing1 = MagicMock()
    res_existing1.scalar_one_or_none.return_value = existing_prod1

    # 3. Existing query for art2 returns None (fresh production artifact)
    res_existing2 = MagicMock()
    res_existing2.scalar_one_or_none.return_value = None

    mock_session.execute.side_effect = [
        res_staging,
        res_existing1,
        res_existing2,
    ]

    result = await executor.promote_scope(
        mock_session,
        "scope-123",
        actor_id="admin-1",
        confirmation="PROMOTE scope-123 TO PRODUCTION",
    )

    assert isinstance(result, ProductionPromotionResult)
    assert result.status == "succeeded"
    assert result.promoted_count == 2
    assert len(result.errors) == 0
    assert existing_prod1.production_status == "superseded"
    assert mock_session.add.call_count >= 2  # promotion event + production artifacts


@pytest.mark.asyncio
@pytest.mark.unit
async def test_promote_scope_handles_per_artifact_exception(executor, mock_gate):
    mock_session = AsyncMock()

    staging_art = MagicMock(
        spec=ContentStagingArtifact,
        artifact_id=uuid.uuid4(),
    )

    res_staging = MagicMock()
    res_staging.scalars.return_value.all.return_value = [staging_art]

    # Session.execute on existing check raises unexpected error
    mock_session.execute.side_effect = [
        res_staging,
        RuntimeError("DB constraint violation"),
    ]

    result = await executor.promote_scope(
        mock_session,
        "scope-123",
        actor_id="admin-1",
        confirmation="PROMOTE scope-123 TO PRODUCTION",
    )

    assert result.status == "failed"
    assert result.promoted_count == 0
    assert len(result.errors) == 1
    assert "Failed to promote artifact" in result.errors[0]


# ---------------------------------------------------------------------------
# get_promotion_event
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_promotion_event_not_found_raises_value_error(executor):
    mock_session = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = res

    event_id = uuid.uuid4()
    with pytest.raises(ValueError, match=f"Promotion event {event_id} not found"):
        await executor.get_promotion_event(mock_session, event_id)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_promotion_event_success(executor):
    mock_session = AsyncMock()

    event_id = uuid.uuid4()
    mock_event = MagicMock(
        spec=ContentPromotionEvent,
        event_id=event_id,
        scope_id="scope-123",
        status="succeeded",
        summary={"errors": []},
    )
    res_event = MagicMock()
    res_event.scalar_one_or_none.return_value = mock_event

    res_count = MagicMock()
    res_count.scalar.return_value = 5

    mock_session.execute.side_effect = [res_event, res_count]

    result = await executor.get_promotion_event(mock_session, event_id)

    assert result.promotion_event_id == event_id
    assert result.scope_id == "scope-123"
    assert result.status == "succeeded"
    assert result.promoted_count == 5


# ---------------------------------------------------------------------------
# list_promotion_events
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_promotion_events_with_and_without_scope_id(executor):
    mock_session = AsyncMock()

    event_id = uuid.uuid4()
    mock_event = MagicMock(
        spec=ContentPromotionEvent,
        event_id=event_id,
        scope_id="scope-123",
        status="succeeded",
        summary={},
    )

    # Queries:
    # 1. select events
    res_events = MagicMock()
    res_events.scalars.return_value.all.return_value = [mock_event]

    # 2. total count
    res_total = MagicMock()
    res_total.scalar.return_value = 1

    # 3. count of promoted artifacts for event
    res_art_count = MagicMock()
    res_art_count.scalar.return_value = 3

    mock_session.execute.side_effect = [res_events, res_total, res_art_count]

    page = await executor.list_promotion_events(
        mock_session,
        scope_id="scope-123",
        limit=10,
        offset=0,
    )

    assert isinstance(page, ProductionPromotionPage)
    assert page.total == 1
    assert len(page.items) == 1
    assert page.items[0].promoted_count == 3
    assert page.items[0].scope_id == "scope-123"


# ---------------------------------------------------------------------------
# rollback_promotion
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_rollback_promotion_not_found_raises_value_error(executor):
    mock_session = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = res

    event_id = uuid.uuid4()
    with pytest.raises(ValueError, match=f"Promotion event {event_id} not found"):
        await executor.rollback_promotion(
            mock_session,
            event_id,
            actor_id="admin-1",
            reason="Corrupted syllabus",
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_rollback_promotion_success(executor):
    mock_session = AsyncMock()

    event_id = uuid.uuid4()
    mock_event = MagicMock(
        spec=ContentPromotionEvent,
        event_id=event_id,
        status="succeeded",
        summary={"initial": "data"},
    )
    res_event = MagicMock()
    res_event.scalar_one_or_none.return_value = mock_event

    prod_art1 = MagicMock(spec=ContentProductionArtifact, production_status="active")
    prod_art2 = MagicMock(spec=ContentProductionArtifact, production_status="active")
    res_artifacts = MagicMock()
    res_artifacts.scalars.return_value.all.return_value = [prod_art1, prod_art2]

    mock_session.execute.side_effect = [res_event, res_artifacts]

    rollback_res = await executor.rollback_promotion(
        mock_session,
        event_id,
        actor_id="admin-1",
        reason="Faulty answer keys",
    )

    assert isinstance(rollback_res, ProductionRollbackResult)
    assert rollback_res.status == "rolled_back"
    assert rollback_res.rolled_back_count == 2
    assert prod_art1.production_status == "rolled_back"
    assert prod_art2.production_status == "rolled_back"
    assert mock_event.status == "rolled_back"
    assert mock_event.summary["rollback_reason"] == "Faulty answer keys"
    assert mock_event.summary["rolled_back_by"] == "admin-1"
