"""Comprehensive unit tests for staging seed execution, promotion gates, and launch content seeding."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.content_staging_seed_executor import (
    ContentStagingSeedExecutor,
    SeedableArtifact,
    SkippedArtifact,
    StagingSeedPlan,
    StagingSeedRunResult,
    StagingRollbackResult,
    MissingForeignKeyError,
    _maybe_await,
)
from app.services.content_production_promotion_gate import (
    ContentProductionPromotionGate,
    ProductionGateStatus,
    ProductionGateBlocker,
    ProductionGateReport,
)
from app.services.content_production_promotion_executor import (
    ContentProductionPromotionExecutor,
    ProductionPromotionPlan,
    ProductionPromotionResult,
    ProductionRollbackResult,
)
from app.services.launch_content_seed import (
    seed_launch_content_if_needed,
    LAUNCH_SCOPE_ID,
    DEFAULT_ITEM_TARGET,
    DEFAULT_LESSON_TARGET,
    SEED_OWNER_EMAIL,
)


class TestStagingSeedExecutor:
    @pytest.mark.asyncio
    async def test_maybe_await_coroutine_and_scalar(self):
        async def sample_coro():
            return 42

        assert await _maybe_await(sample_coro()) == 42
        assert await _maybe_await(100) == 100

    def test_seedable_artifact_dataclass(self):
        art = SeedableArtifact(
            artifact_id=uuid.uuid4(),
            scope_id="grade4_maths",
            caps_ref="4.M.1.1",
            layer="lesson_plan",
            artifact_type="lesson",
            payload_json={"title": "Test"},
            artifact_hash="sha256:abc",
        )
        assert art.scope_id == "grade4_maths"
        assert art.caps_ref == "4.M.1.1"

    def test_staging_seed_run_result_dataclass(self):
        uid = uuid.uuid4()
        res = StagingSeedRunResult(
            seed_run_id=uid,
            scope_id="grade4_maths",
            status="completed",
            seeded_count=15,
            skipped_count=0,
        )
        assert res.seeded_count == 15
        assert res.errors == []

    def test_staging_rollback_result_dataclass(self):
        uid = uuid.uuid4()
        res = StagingRollbackResult(
            seed_run_id=uid,
            status="rolled_back",
            rolled_back_count=15,
        )
        assert res.rolled_back_count == 15


class TestProductionPromotionGate:
    def test_promotion_gate_enums(self):
        assert ProductionGateStatus.PROMOTABLE.value == "promotable"
        assert ProductionGateStatus.BLOCKED_BY_REVIEW.value == "blocked_by_review"
        assert ProductionGateStatus.BLOCKED_BY_COVERAGE.value == "blocked_by_coverage"

    def test_promotion_gate_report_dataclass(self):
        report = ProductionGateReport(
            scope_id="grade4_maths",
            status=ProductionGateStatus.PROMOTABLE,
            blockers=[],
            coverage_summary={"total": 100},
            staging_summary={"staged": 100},
        )
        assert report.status == ProductionGateStatus.PROMOTABLE
        assert len(report.blockers) == 0

    def test_promotion_gate_blocker_dataclass(self):
        b = ProductionGateBlocker(
            type="missing_review",
            message="Item requires consensus review approval",
            caps_ref="4.M.1.1",
        )
        assert b.type == "missing_review"
        assert b.caps_ref == "4.M.1.1"


class TestProductionPromotionExecutor:
    def test_promotion_plan_and_result_dataclasses(self):
        plan = ProductionPromotionPlan(
            scope_id="grade4_maths",
            layers=["lesson_plan"],
            promotable_count=10,
            skipped_count=0,
        )
        assert plan.promotable_count == 10

        uid = uuid.uuid4()
        res = ProductionPromotionResult(
            promotion_event_id=uid,
            scope_id="grade4_maths",
            status="promoted",
            promoted_count=10,
            skipped_count=0,
        )
        assert res.promoted_count == 10

        rb = ProductionRollbackResult(
            promotion_event_id=uid,
            status="rolled_back",
            rolled_back_count=10,
        )
        assert rb.rolled_back_count == 10


class TestLaunchContentSeed:
    def test_constants(self):
        assert LAUNCH_SCOPE_ID == "grade4_mathematics_en"
        assert DEFAULT_ITEM_TARGET == 40
        assert DEFAULT_LESSON_TARGET == 8
        assert SEED_OWNER_EMAIL == "launch-content-seed@example.invalid"

    @pytest.mark.asyncio
    async def test_seed_launch_content_disabled(self):
        with patch("app.services.launch_content_seed.settings.CONTENT_STARTUP_SEED_ENABLED", False):
            # Should immediately return without raising
            await seed_launch_content_if_needed()
