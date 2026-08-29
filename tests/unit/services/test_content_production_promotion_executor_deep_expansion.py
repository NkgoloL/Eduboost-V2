import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.content_production_promotion_executor import (
    ProductionPromotionPlan,
    ProductionPromotionResult,
    ProductionPromotionPage,
    ProductionRollbackResult,
    ContentProductionPromotionExecutor,
)


def test_production_promotion_dataclasses():
    plan = ProductionPromotionPlan(
        scope_id="scope-1",
        layers=["lesson_content"],
        promotable_count=10,
        skipped_count=0,
    )
    assert plan.promotable_count == 10

    event_id = uuid.uuid4()
    res = ProductionPromotionResult(
        promotion_event_id=event_id,
        scope_id="scope-1",
        status="promoted",
        promoted_count=10,
        skipped_count=0,
    )
    assert res.promotion_event_id == event_id

    page = ProductionPromotionPage(total=1, limit=50, offset=0, items=[res])
    assert page.total == 1

    rollback = ProductionRollbackResult(
        promotion_event_id=event_id,
        status="rolled_back",
        rolled_back_count=10,
    )
    assert rollback.status == "rolled_back"


@pytest.mark.asyncio
async def test_dry_run_promotion_gate_blocked():
    mock_gate = AsyncMock()
    gate_report = MagicMock()
    gate_report.status.value = "blocked"
    blocker = MagicMock()
    blocker.message = "Missing answer key verifications"
    gate_report.blockers = [blocker]
    mock_gate.evaluate_scope.return_value = gate_report

    executor = ContentProductionPromotionExecutor(gate=mock_gate)
    session = AsyncMock()

    with pytest.raises(ValueError, match="Cannot dry-run promotion: gate status is blocked"):
        await executor.dry_run_promotion(session, "scope-1", actor_id="admin")
