"""Comprehensive unit tests for Content Factory router, Review Governance, Batch Generation, and Promotion Gates."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentGenerationRun,
    ContentGenerationTask,
    ContentReviewAction,
    ContentReviewAssignment,
    ContentReviewDecision,
    ContentStateTransitionEvent,
)
from app.domain.content_coverage import ContentLayer
from app.services.content_review_governance import (
    ReviewGovernancePolicy,
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
)
from app.services.batch_generation import (
    BatchGenerationEngine,
    GenerationTaskSpec,
    RunResult,
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
from app.services.content_staging_seed_executor import (
    ContentStagingSeedExecutor,
    SeedableArtifact,
    SkippedArtifact,
    StagingSeedPlan,
    StagingSeedRunResult,
)


# ---------------------------------------------------------------------------
# Review Governance Policy Tests
# ---------------------------------------------------------------------------

class TestReviewGovernancePolicy:
    def test_default_policy(self):
        pol = ReviewGovernancePolicy()
        assert pol.quorum_threshold == 3
        assert pol.rubric_id == "educator-content-review"
        assert pol.stale_after_hours == 72
        assert pol.creator_approval_counts is False
        assert pol.direct_publish_allowed is False

    def test_from_environment_valid(self):
        with patch.dict(os.environ, {
            "CONTENT_CONSENSUS_THRESHOLD": "4",
            "CONTENT_CONSENSUS_TIMEOUT_HOURS": "48",
            "CONTENT_CREATOR_APPROVAL_COUNTS": "true",
            "CONTENT_DIRECT_PUBLISH_ALLOWED": "1",
        }):
            pol = ReviewGovernancePolicy.from_environment()
            assert pol.quorum_threshold == 4
            assert pol.stale_after_hours == 48
            assert pol.creator_approval_counts is True
            assert pol.direct_publish_allowed is True

    def test_from_environment_invalid_threshold(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "1"}):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_THRESHOLD must be between 2 and 10"):
                ReviewGovernancePolicy.from_environment()

        with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "15"}):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_THRESHOLD must be between 2 and 10"):
                ReviewGovernancePolicy.from_environment()

    def test_from_environment_invalid_stale_hours(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_TIMEOUT_HOURS": "0"}):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_TIMEOUT_HOURS must be positive"):
                ReviewGovernancePolicy.from_environment()

    def test_required_rubric_criteria_completeness(self):
        assert "caps_alignment" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "factual_accuracy" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "answer_key_correctness" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "source_grounding" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "personal_information" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert len(REQUIRED_APPROVAL_RUBRIC_CRITERIA) == 10


# ---------------------------------------------------------------------------
# Production Promotion Gate & Executor Tests
# ---------------------------------------------------------------------------

class TestProductionPromotionGate:
    def test_promotion_gate_init(self):
        mock_cov = MagicMock()
        gate = ContentProductionPromotionGate(coverage_service=mock_cov)
        assert gate.coverage_service == mock_cov

    def test_production_gate_report_and_blockers(self):
        blocker = ProductionGateBlocker(type="review", message="Pending consensus")
        assert blocker.type == "review"
        assert blocker.message == "Pending consensus"

        report = ProductionGateReport(
            scope_id="math-g4",
            status=ProductionGateStatus.PROMOTABLE,
            blockers=[blocker],
        )
        assert report.scope_id == "math-g4"
        assert report.status == ProductionGateStatus.PROMOTABLE
        assert len(report.blockers) == 1


class TestProductionPromotionExecutor:
    def test_executor_init(self):
        mock_gate = MagicMock()
        executor = ContentProductionPromotionExecutor(gate=mock_gate)
        assert executor.gate == mock_gate

    def test_rollback_result_dataclass(self):
        eid = uuid.uuid4()
        rr = ProductionRollbackResult(
            promotion_event_id=eid,
            status="completed",
            rolled_back_count=5,
        )
        assert rr.promotion_event_id == eid
        assert rr.rolled_back_count == 5


class TestStagingSeedExecutor:
    def test_staging_seed_init(self):
        mock_factory = MagicMock()
        executor = ContentStagingSeedExecutor(factory_service=mock_factory)
        assert executor.factory_service == mock_factory

    def test_staging_seed_plan_dataclasses(self):
        art_id = uuid.uuid4()
        seedable = SeedableArtifact(
            artifact_id=art_id,
            scope_id="scope1",
            caps_ref="MATH.G4",
            layer="diagnostic_items",
            artifact_type="item",
            payload_json={"q": 1},
            artifact_hash="hash123",
        )
        skipped = SkippedArtifact(artifact_id=art_id, reason="already_seeded")
        plan = StagingSeedPlan(
            scope_id="scope1",
            layers=["diagnostic_items"],
            seedable=[seedable],
            skipped=[skipped],
        )
        assert plan.scope_id == "scope1"
        assert len(plan.seedable) == 1
        assert len(plan.skipped) == 1


# ---------------------------------------------------------------------------
# Batch Generation Engine Tests
# ---------------------------------------------------------------------------

class TestBatchGenerationEngine:
    def test_generation_task_spec(self):
        spec = GenerationTaskSpec(
            caps_ref="MATH.G4.T1.1",
            content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
            content_type="diagnostic_item",
            count=3,
        )
        assert spec.caps_ref == "MATH.G4.T1.1"
        assert spec.count == 3
        assert spec.language == "en"

    def test_run_result(self):
        run_id = uuid.uuid4()
        rr = RunResult(
            run_id=run_id,
            total_tasks=10,
            succeeded=8,
            failed=1,
            safety_blocked=1,
            skipped=0,
        )
        assert rr.run_id == run_id
        assert rr.succeeded == 8

    def test_engine_init(self):
        mock_router = MagicMock()
        engine = BatchGenerationEngine(provider_router=mock_router)
        assert engine._router == mock_router
