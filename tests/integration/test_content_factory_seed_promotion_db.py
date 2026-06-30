"""tests/integration/test_content_factory_seed_promotion_db.py
─────────────────────────────────────────────────────────────────────────────
DB-backed seed/promotion gate tests.

Verifies that:
  - Staging seed fails when artifact coverage is RED (no approved artifacts)
  - Dry-run returns status="blocked" and records a ContentSeedRun row
  - Staging seed succeeds when coverage gate is GREEN (all approved)
  - Production promotion fails if coverage gate is RED
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations


import pytest
from sqlalchemy import select

from app.domain.content_coverage import (
    CapsRefCoverageReport,
    ContentLayer,
    CoverageLayerCounts,
    CoverageLayerStatus,
    ScopeCoverageLayerSummary,
    ScopeCoverageReport,
    ScopeCoverageSummary,
)
from app.models.content_factory import ContentSeedRun
from app.services.content_seed_promotion import ContentSeedPromotionService

pytestmark = pytest.mark.integration


# ── fake coverage service ─────────────────────────────────────────────────────

class _FakeCoverageService:
    """Returns a synthetic ScopeCoverageReport with a fixed coverage status."""

    def __init__(self, status: CoverageLayerStatus) -> None:
        self._status = status

    async def get_scope_coverage(
        self,
        scope_id: str,
        layers: list[ContentLayer] | None = None,
    ) -> ScopeCoverageReport:
        selected = layers or [ContentLayer.DIAGNOSTIC_ITEMS]
        is_green = self._status == CoverageLayerStatus.GREEN
        layer_counts = CoverageLayerCounts(
            target=40,
            approved=40 if is_green else 0,
            status=self._status,
            coverage_ratio=1.0 if is_green else 0.0,
        )
        return ScopeCoverageReport(
            scope_id=scope_id,
            grade=4,
            subject_code="M",
            language="en",
            summary=ScopeCoverageSummary(
                total_caps_refs=1,
                green_refs=1 if is_green else 0,
                amber_refs=0,
                red_refs=0 if is_green else 1,
                not_configured_refs=0,
            ),
            layers={layer: ScopeCoverageLayerSummary(
                target_total=40,
                approved_total=40 if is_green else 0,
                coverage_ratio=1.0 if is_green else 0.0,
            ) for layer in selected},
            per_caps_ref=[
                CapsRefCoverageReport(
                    scope_id=scope_id,
                    caps_ref="4.M.1.1",
                    layers={layer: layer_counts for layer in selected},
                )
            ],
        )


# ── tests ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dry_run_seed_blocked_when_coverage_red(db_session):
    """Dry-run seed records a ContentSeedRun row with status=blocked."""
    service = ContentSeedPromotionService(_FakeCoverageService(CoverageLayerStatus.RED))

    run = await service.dry_run_seed(db_session, "grade4_mathematics_en")
    await db_session.flush()

    assert run.seed_run_id is not None
    assert run.status == "blocked"
    assert run.dry_run is True

    # Verify persisted row
    result = await db_session.execute(
        select(ContentSeedRun).where(ContentSeedRun.seed_run_id == run.seed_run_id)
    )
    stored = result.scalar_one()
    assert stored.status == "blocked"


@pytest.mark.asyncio
async def test_staging_seed_raises_when_coverage_red(db_session):
    """seed_staging raises ValueError when coverage gate is RED."""
    service = ContentSeedPromotionService(_FakeCoverageService(CoverageLayerStatus.RED))

    with pytest.raises(ValueError, match="Staging seed gate failed"):
        await service.seed_staging(db_session, "grade4_mathematics_en", actor_id="admin-1")


@pytest.mark.asyncio
async def test_dry_run_seed_passed_when_coverage_green(db_session):
    """Dry-run seed records status=passed when all coverage layers are GREEN."""
    service = ContentSeedPromotionService(_FakeCoverageService(CoverageLayerStatus.GREEN))

    run = await service.dry_run_seed(db_session, "grade4_mathematics_en")
    await db_session.flush()

    assert run.status == "passed"


@pytest.mark.asyncio
async def test_staging_seed_succeeds_when_coverage_green(db_session):
    """seed_staging returns a ContentSeedRun with status=seeded_staging when GREEN."""
    service = ContentSeedPromotionService(_FakeCoverageService(CoverageLayerStatus.GREEN))

    run = await service.seed_staging(
        db_session, "grade4_mathematics_en", actor_id="admin-1"
    )
    await db_session.flush()

    assert run.status == "seeded_staging"
    assert run.dry_run is False

    result = await db_session.execute(
        select(ContentSeedRun).where(ContentSeedRun.seed_run_id == run.seed_run_id)
    )
    stored = result.scalar_one()
    assert stored.status == "seeded_staging"
    assert stored.summary.get("actor_id") == "admin-1"


@pytest.mark.asyncio
async def test_production_promotion_raises_when_coverage_red(db_session):
    """promote_production raises ValueError when coverage gate is not GREEN."""
    service = ContentSeedPromotionService(_FakeCoverageService(CoverageLayerStatus.RED))

    with pytest.raises(ValueError, match="Production promotion gate failed"):
        await service.promote_production(
            db_session, "grade4_mathematics_en", actor_id="admin-1"
        )
