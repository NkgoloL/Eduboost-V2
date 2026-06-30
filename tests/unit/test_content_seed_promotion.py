import pytest
from uuid import UUID

from app.domain.content_coverage import ContentLayer, CoverageLayerCounts, CoverageLayerStatus, ScopeCoverageLayerSummary, ScopeCoverageReport, ScopeCoverageSummary, CapsRefCoverageReport
from app.services.content_production_promotion_gate import ProductionGateStatus
from app.services.content_seed_promotion import ContentSeedPromotionService


class FakeCoverageService:
    def __init__(self, status: CoverageLayerStatus, approved: int | None = None) -> None:
        self.status = status
        self.approved = approved

    async def get_scope_coverage(self, scope_id, layers=None):
        selected = layers or [ContentLayer.DIAGNOSTIC_ITEMS]
        approved = self.approved
        if approved is None:
            approved = 1 if self.status == CoverageLayerStatus.GREEN else 0
        return ScopeCoverageReport(
            scope_id=scope_id,
            grade=4,
            subject_code="MAT",
            language="en",
            summary=ScopeCoverageSummary(total_caps_refs=1, green_refs=1 if self.status == CoverageLayerStatus.GREEN else 0, amber_refs=1 if self.status == CoverageLayerStatus.AMBER else 0, red_refs=1 if self.status == CoverageLayerStatus.RED else 0, not_configured_refs=0),
            layers={layer: ScopeCoverageLayerSummary(target_total=1, approved_total=approved, coverage_ratio=float(approved)) for layer in selected},
            per_caps_ref=[CapsRefCoverageReport(scope_id=scope_id, caps_ref="4.M.1.1", layers={layer: CoverageLayerCounts(target=1, approved=approved, status=self.status) for layer in selected})],
        )


class FakeSeedExecutor:
    async def seed_staging(self, session, scope_id, *, layers=None, actor_id, allow_partial=True):
        return type(
            "SeedResult",
            (),
            {
                "seed_run_id": UUID("00000000-0000-0000-0000-000000000123"),
                "scope_id": scope_id,
                "status": "partially_seeded_staging",
                "seeded_count": 1,
                "skipped_count": 1,
                "errors": ["coverage is amber"],
            },
        )()


class PassingVerificationService:
    async def verify_scope_staging(self, session, scope_id):
        return type("Report", (), {"passed": True, "errors": [], "staged_artifacts_count": 1})()


class FailingVerificationService:
    async def verify_scope_staging(self, session, scope_id):
        return type("Report", (), {"passed": False, "errors": ["missing staging record"], "staged_artifacts_count": 0})()


class FakeProductionGate:
    def __init__(self, status: ProductionGateStatus = ProductionGateStatus.PROMOTABLE) -> None:
        self.status = status

    async def evaluate_scope(self, session, scope_id, *, layers=None):
        from app.services.content_production_promotion_gate import ProductionGateBlocker, ProductionGateReport
        if self.status == ProductionGateStatus.PROMOTABLE:
            return ProductionGateReport(
                scope_id=scope_id,
                status=ProductionGateStatus.PROMOTABLE,
                blockers=[],
                coverage_summary={},
                staging_summary={},
            )
        else:
            return ProductionGateReport(
                scope_id=scope_id,
                status=self.status,
                blockers=[ProductionGateBlocker(type="test", message="Test blocker")],
                coverage_summary={},
                staging_summary={},
            )


class Result:
    def scalars(self):
        return self
    def all(self):
        return []


class Session:
    def add(self, obj):
        self.obj = obj
    async def get(self, model, key):
        return getattr(self, "obj", None)
    async def flush(self):
        return None
    async def execute(self, stmt):
        return Result()


@pytest.mark.asyncio
async def test_seed_gate_fails_when_coverage_is_red() -> None:
    service = ContentSeedPromotionService(FakeCoverageService(CoverageLayerStatus.RED))
    with pytest.raises(ValueError):
        await service.seed_staging(Session(), "grade4_mathematics_en", "admin")


@pytest.mark.asyncio
async def test_dry_run_seed_records_blocked_result() -> None:
    service = ContentSeedPromotionService(FakeCoverageService(CoverageLayerStatus.RED))
    run = await service.dry_run_seed(Session(), "grade4_mathematics_en")
    assert run.status == "partial"


@pytest.mark.asyncio
async def test_staging_allows_partial_seed_with_blockers() -> None:
    service = ContentSeedPromotionService(
        FakeCoverageService(CoverageLayerStatus.AMBER, approved=1),
        seed_executor=FakeSeedExecutor(),
    )
    run = await service.seed_staging(Session(), "grade4_mathematics_en", "admin", allow_partial=True)
    assert run.status == "partially_seeded_staging"


@pytest.mark.asyncio
async def test_production_promotion_rejects_unverified_staging() -> None:
    service = ContentSeedPromotionService(
        FakeCoverageService(CoverageLayerStatus.GREEN),
        verification_service=FailingVerificationService(),
        production_gate=FakeProductionGate(),
    )
    with pytest.raises(ValueError, match="Staging verification failed"):
        await service.promote_production(Session(), "grade4_mathematics_en", "admin")


@pytest.mark.asyncio
async def test_production_promotion_requires_full_gate_report() -> None:
    service = ContentSeedPromotionService(
        FakeCoverageService(CoverageLayerStatus.GREEN),
        verification_service=PassingVerificationService(),
        production_gate=FakeProductionGate(status=ProductionGateStatus.BLOCKED_BY_COVERAGE),
    )
    with pytest.raises(ValueError, match="Production promotion gate failed"):
        await service.promote_production(Session(), "grade4_mathematics_en", "admin")


@pytest.mark.asyncio
async def test_production_promotion_passes_with_full_gate_report() -> None:
    service = ContentSeedPromotionService(
        FakeCoverageService(CoverageLayerStatus.GREEN),
        verification_service=PassingVerificationService(),
        production_gate=FakeProductionGate(status=ProductionGateStatus.PROMOTABLE),
    )
    result = await service.promote_production(Session(), "grade4_mathematics_en", "admin")
    assert result.passed
