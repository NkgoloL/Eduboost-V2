"""Comprehensive unit tests for ContentSeedPromotionService and GateResult."""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.content_coverage import (
    CapsRefCoverageReport,
    ContentLayer,
    CoverageLayerCounts,
    CoverageLayerStatus,
    ScopeCoverageReport,
    ScopeCoverageSummary,
)
from app.services.content_seed_promotion import (
    ContentSeedPromotionService,
    GateResult,
)


class TestContentSeedPromotion:
    def test_gate_result_dataclass(self):
        res = GateResult(
            passed=True,
            errors=[],
            summary={"stageable_approved": 40},
        )
        assert res.passed is True
        assert len(res.errors) == 0
        assert res.summary["stageable_approved"] == 40

    def test_content_seed_promotion_service_init(self):
        mock_coverage = MagicMock()
        mock_verification = MagicMock()
        mock_executor = MagicMock()
        mock_gate = MagicMock()

        service = ContentSeedPromotionService(
            coverage_service=mock_coverage,
            verification_service=mock_verification,
            seed_executor=mock_executor,
            production_gate=mock_gate,
        )
        assert service.coverage_service == mock_coverage
        assert service.verification_service == mock_verification
        assert service.seed_executor == mock_executor
        assert service.production_gate == mock_gate


class TestContentSeedPromotionExecution:
    @pytest.mark.asyncio
    async def test_dry_run_seed_branches(self):
        mock_coverage = AsyncMock()
        mock_coverage.get_scope_coverage.return_value = ScopeCoverageReport(
            scope_id="s1",
            grade=4,
            subject_code="MATH",
            language="en",
            summary=ScopeCoverageSummary(total_caps_refs=1, green_refs=1, amber_refs=0, red_refs=0, not_configured_refs=0),
            layers={},
            per_caps_ref=[
                CapsRefCoverageReport(
                    scope_id="s1",
                    caps_ref="4.M.1.1",
                    layers={
                        ContentLayer.LESSONS: CoverageLayerCounts(
                            target=10, approved=10, pending_review=0, rejected=0, generated=0,
                            status=CoverageLayerStatus.GREEN, coverage_ratio=1.0,
                        )
                    },
                )
            ],
        )

        service = ContentSeedPromotionService(coverage_service=mock_coverage)
        session = AsyncMock()

        # 1. Full green -> status "passed"
        run_passed = await service.dry_run_seed(session, "s1", layers=[ContentLayer.LESSONS])
        assert run_passed.status == "passed"
        assert run_passed.dry_run is True
        session.add.assert_called()
        session.flush.assert_called()

        # 2. Non-green -> status "partial"
        mock_coverage.get_scope_coverage.return_value = ScopeCoverageReport(
            scope_id="s1",
            grade=4,
            subject_code="MATH",
            language="en",
            summary=ScopeCoverageSummary(total_caps_refs=1, green_refs=0, amber_refs=1, red_refs=0, not_configured_refs=0),
            layers={},
            per_caps_ref=[
                CapsRefCoverageReport(
                    scope_id="s1",
                    caps_ref="4.M.1.1",
                    layers={
                        ContentLayer.LESSONS: CoverageLayerCounts(
                            target=10, approved=5, pending_review=2, rejected=0, generated=0,
                            status=CoverageLayerStatus.AMBER, coverage_ratio=0.5,
                        )
                    },
                )
            ],
        )
        run_partial = await service.dry_run_seed(session, "s1", layers=[ContentLayer.LESSONS])
        assert run_partial.status == "partial"

    @pytest.mark.asyncio
    async def test_seed_staging_branches(self):
        mock_coverage = AsyncMock()
        mock_executor = AsyncMock()
        service = ContentSeedPromotionService(
            coverage_service=mock_coverage,
            seed_executor=mock_executor,
        )
        session = AsyncMock()

        # 1. Gate fails and stageable_count <= 0 -> raises ValueError
        with patch.object(service, "_seed_gate", return_value=GateResult(False, ["Coverage amber"], {"stageable_approved": 0})):
            with pytest.raises(ValueError, match="Staging seed gate failed"):
                await service.seed_staging(session, "s1", "admin", allow_partial=False)

        # 2. Gate partial with stageable_count > 0 and allow_partial=True
        seed_id = uuid.uuid4()
        mock_executor.seed_staging.return_value = SimpleNamespace(
            seed_run_id=seed_id,
            status="seeded",
            seeded_count=5,
            skipped_count=0,
            errors=[],
        )
        session.get.return_value = None  # creates new ContentSeedRun

        with patch.object(service, "_seed_gate", return_value=GateResult(False, ["Coverage amber"], {"stageable_approved": 5})):
            run = await service.seed_staging(session, "s1", "admin", allow_partial=True)
            assert run.seed_run_id == seed_id
            assert run.status == "seeded"
            session.add.assert_called()
            session.flush.assert_called()

    @pytest.mark.asyncio
    async def test_promote_production_branches(self):
        mock_coverage = AsyncMock()
        mock_verification = AsyncMock()
        mock_gate = AsyncMock()

        service = ContentSeedPromotionService(
            coverage_service=mock_coverage,
            verification_service=mock_verification,
            production_gate=mock_gate,
        )
        session = AsyncMock()

        # 1. Gate report status != "promotable" -> ValueError
        mock_gate.evaluate_scope.return_value = SimpleNamespace(
            status=SimpleNamespace(value="blocked_by_coverage"),
            blockers=[SimpleNamespace(message="Missing approved lessons")],
        )
        with pytest.raises(ValueError, match="Production promotion gate failed: blocked_by_coverage"):
            await service.promote_production(session, "s1", "admin")

        # 2. Gate promotable but staging verification fails -> ValueError
        mock_gate.evaluate_scope.return_value = SimpleNamespace(
            status=SimpleNamespace(value="promotable"),
            coverage_summary={"cov": 100},
            staging_summary={"stg": 100},
            blockers=[],
        )
        mock_verification.verify_scope_staging.return_value = SimpleNamespace(
            passed=False,
            errors=["Missing staging rows"],
            staged_artifacts_count=0,
        )
        with pytest.raises(ValueError, match="Staging verification failed"):
            await service.promote_production(session, "s1", "admin")

        # 3. Clean promotion success
        mock_verification.verify_scope_staging.return_value = SimpleNamespace(
            passed=True,
            errors=[],
            staged_artifacts_count=10,
        )
        res = await service.promote_production(session, "s1", "admin")
        assert res.passed is True
        assert res.errors == []
        assert res.summary["cov"] == 100
