"""Content Factory seed and promotion gate service."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.content_coverage import ContentLayer, CoverageLayerStatus
from app.models.content_factory import ContentSeedRun
from app.services.content_coverage_service import ContentCoverageService
from app.services.content_production_promotion_gate import ContentProductionPromotionGate
from app.services.content_staging_read_verification import ContentStagingReadVerificationService
from app.services.content_staging_seed_executor import ContentStagingSeedExecutor


@dataclass(frozen=True)
class GateResult:
    passed: bool
    errors: list[str]
    summary: dict[str, Any]


class ContentSeedPromotionService:
    def __init__(
        self,
        coverage_service: ContentCoverageService,
        verification_service: ContentStagingReadVerificationService | None = None,
        seed_executor: ContentStagingSeedExecutor | None = None,
        production_gate: ContentProductionPromotionGate | None = None,
    ) -> None:
        self.coverage_service = coverage_service
        self.verification_service = verification_service or ContentStagingReadVerificationService()
        self.seed_executor = seed_executor or ContentStagingSeedExecutor()
        self.production_gate = production_gate or ContentProductionPromotionGate(coverage_service=coverage_service)

    async def dry_run_seed(self, session: AsyncSession, scope_id: str, layers: list[ContentLayer] | None = None) -> ContentSeedRun:
        gate = await self._seed_gate(session, scope_id, layers)
        run = ContentSeedRun(
            seed_run_id=uuid.uuid4(),
            scope_id=scope_id,
            dry_run=True,
            status="passed" if gate.passed else "partial",
            summary=gate.summary | {"errors": gate.errors},
        )
        session.add(run)
        await session.flush()
        return run

    async def seed_staging(
        self,
        session: AsyncSession,
        scope_id: str,
        actor_id: str,
        *,
        layers: list[ContentLayer] | None = None,
        allow_partial: bool = True,
    ) -> ContentSeedRun:
        gate = await self._seed_gate(session, scope_id, layers)
        stageable_count = int(gate.summary.get("stageable_approved", 0))
        if not gate.passed and (not allow_partial or stageable_count <= 0):
            raise ValueError("Staging seed gate failed: " + "; ".join(gate.errors))

        layer_values = [layer.value for layer in layers] if layers else None
        result = await self.seed_executor.seed_staging(
            session,
            scope_id,
            layers=layer_values,
            actor_id=actor_id,
            allow_partial=allow_partial,
        )
        run = await session.get(ContentSeedRun, result.seed_run_id)
        if run is None:
            run = ContentSeedRun(
                seed_run_id=result.seed_run_id,
                scope_id=scope_id,
                dry_run=False,
                status=result.status,
                summary={
                    "actor_id": actor_id,
                    "seeded_count": result.seeded_count,
                    "skipped_count": result.skipped_count,
                    "errors": result.errors,
                },
            )
            session.add(run)
            await session.flush()
        return run

    async def verify_staging_seed(self, session: AsyncSession, scope_id: str) -> GateResult:
        # Verify read-visibility of staging
        report = await self.verification_service.verify_scope_staging(session, scope_id)
        if not report.passed:
            return GateResult(False, report.errors, {"scope_id": scope_id, "staged_artifacts_count": report.staged_artifacts_count})
        return GateResult(True, [], {"scope_id": scope_id, "staged_artifacts_count": report.staged_artifacts_count})

    async def promote_production(self, session: AsyncSession, scope_id: str, actor_id: str) -> GateResult:
        # Use the production promotion gate to evaluate scope eligibility
        gate_report = await self.production_gate.evaluate_scope(session, scope_id)

        if gate_report.status.value != "promotable":
            errors = [b.message for b in gate_report.blockers]
            raise ValueError(
                f"Production promotion gate failed: {gate_report.status.value}. "
                + "; ".join(errors)
            )

        # Verify staging seed
        verification = await self.verify_staging_seed(session, scope_id)
        if not verification.passed:
            raise ValueError("Production promotion gate failed: Staging verification failed. " + "; ".join(verification.errors))

        return GateResult(True, [], gate_report.coverage_summary | gate_report.staging_summary)

    async def _seed_gate(self, session: AsyncSession, scope_id: str, layers: list[ContentLayer] | None) -> GateResult:
        layers = layers or list(ContentLayer)
        coverage = await self.coverage_service.get_scope_coverage(scope_id, layers=layers)
        errors: list[str] = []
        stageable_approved = 0
        blocking_artifact_count = 0

        for caps_ref in coverage.per_caps_ref:
            for item in layers:
                counts = caps_ref.layers.get(item)
                if counts is None:
                    continue
                stageable_approved += int(counts.approved or 0)
                if counts.status != CoverageLayerStatus.GREEN:
                    blocking_artifact_count += 1
                    errors.append(f"{caps_ref.caps_ref}:{item.value} coverage is {counts.status.value}.")
        # A simple check: do we have full green coverage?
        return GateResult(not errors, errors, {"scope_id": scope_id, "layers": [item.value for item in layers], "stageable_approved": stageable_approved, "blocking_artifact_count": blocking_artifact_count})
