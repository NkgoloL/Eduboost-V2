import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.domain.content_coverage import ContentLayer, CoverageLayerStatus
from app.services.content_production_promotion_gate import (
    ProductionGateStatus,
    ProductionGateBlocker,
    ProductionGateReport,
    ContentProductionPromotionGate,
)


def test_production_gate_enums_and_dataclasses():
    assert ProductionGateStatus.PROMOTABLE == "promotable"
    assert ProductionGateStatus.BLOCKED_BY_COVERAGE == "blocked_by_coverage"

    blocker = ProductionGateBlocker(type="coverage", message="Coverage red")
    assert blocker.type == "coverage"

    report = ProductionGateReport(
        scope_id="scope-1",
        status=ProductionGateStatus.PROMOTABLE,
    )
    assert report.status == ProductionGateStatus.PROMOTABLE


@pytest.mark.asyncio
async def test_assert_promotable_raises_when_blocked():
    mock_cov = AsyncMock()
    gate = ContentProductionPromotionGate(coverage_service=mock_cov)
    session = AsyncMock()

    mock_report = ProductionGateReport(
        scope_id="scope-1",
        status=ProductionGateStatus.BLOCKED_BY_REVIEW,
        blockers=[ProductionGateBlocker(type="review", message="Pending educator reviews")],
    )
    gate.evaluate_scope = AsyncMock(return_value=mock_report)

    with pytest.raises(ValueError, match="Production promotion gate failed for scope scope-1: blocked_by_review"):
        await gate.assert_promotable(session, "scope-1")
