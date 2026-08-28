"""Comprehensive unit tests for ContentProductionPromotionExecutor dataclasses and initialization."""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
import pytest

from app.services.content_production_promotion_executor import (
    ProductionPromotionPlan,
    ProductionPromotionResult,
    ProductionPromotionPage,
    ProductionRollbackResult,
    ContentProductionPromotionExecutor,
)


class TestProductionPromotionDataclasses:
    def test_production_promotion_plan(self):
        plan = ProductionPromotionPlan(
            scope_id="grade4_maths",
            layers=["diagnostic_items", "lessons"],
            promotable_count=50,
            skipped_count=0,
            skipped=[],
        )
        assert plan.scope_id == "grade4_maths"
        assert plan.promotable_count == 50
        assert len(plan.layers) == 2

    def test_production_promotion_result(self):
        peid = uuid.uuid4()
        res = ProductionPromotionResult(
            promotion_event_id=peid,
            scope_id="grade4_maths",
            status="completed",
            promoted_count=50,
            skipped_count=0,
            errors=[],
        )
        assert res.promotion_event_id == peid
        assert res.promoted_count == 50
        assert res.status == "completed"

    def test_production_promotion_page(self):
        page = ProductionPromotionPage(
            total=10,
            limit=5,
            offset=0,
            items=[],
        )
        assert page.total == 10
        assert page.limit == 5
        assert page.offset == 0

    def test_production_rollback_result(self):
        peid = uuid.uuid4()
        res = ProductionRollbackResult(
            promotion_event_id=peid,
            status="rolled_back",
            rolled_back_count=50,
        )
        assert res.promotion_event_id == peid
        assert res.rolled_back_count == 50

    def test_executor_init(self):
        mock_gate = MagicMock()
        executor = ContentProductionPromotionExecutor(gate=mock_gate)
        assert executor.gate == mock_gate
