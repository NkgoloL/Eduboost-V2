"""All-scope staging readiness verification for Content Factory."""
from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentStagingVerificationRun,
    ContentStagingVerificationScopeResult,
)
from app.services.content_scope_registry import ContentScopeRegistry


class StagingReadinessStatus(str, Enum):
    READY_FOR_STAGING = "ready_for_staging"
    PARTIALLY_STAGEABLE = "partially_stageable"
    BLOCKED_BY_COVERAGE = "blocked_by_coverage"
    BLOCKED_BY_REVIEW = "blocked_by_review"
    BLOCKED_BY_PROVENANCE = "blocked_by_provenance"
    BLOCKED_BY_VALIDATION = "blocked_by_validation"
    BLOCKED_BY_SOURCE_QUALITY = "blocked_by_source_quality"
    BLOCKED_BY_LICENSE = "blocked_by_license"
    BLOCKED_BY_MISSING_TARGETS = "blocked_by_missing_targets"
    BLOCKED_BY_MISSING_SCOPE = "blocked_by_missing_scope"
    NOT_CONFIGURED = "not_configured"


class BlockerSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


class ScopeBlocker(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: str
    severity: BlockerSeverity = BlockerSeverity.BLOCKING
    layer: str | None = None
    caps_ref: str | None = None
    required: int | None = None
    approved: int | None = None
    pending_review: int | None = None
    generated: int | None = None
    validation_failed: int | None = None
    rejected: int | None = None
    quarantined: int | None = None
    seeded_staging: int | None = None
    promoted_production: int | None = None
    message: str | None = None


class LayerReadinessSummary(BaseModel):
    layer: str
    caps_ref: str
    target: int = 0
    approved: int = 0
    pending_review: int = 0
    generated: int = 0
    validation_failed: int = 0
    rejected: int = 0
    quarantined: int = 0
    seeded_staging: int = 0
    promoted_production: int = 0
    stageable: int = 0
    invalid_provenance: int = 0
    invalid_license: int = 0
    low_source_quality: int = 0
    status: StagingReadinessStatus


class ScopeStagingVerificationReport(BaseModel):
    scope_id: str
    status: StagingReadinessStatus
    can_seed_staging: bool
    can_promote_production: bool
    blockers: list[ScopeBlocker] = Field(default_factory=list)
    layers: list[LayerReadinessSummary] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)


class AllScopeStagingVerificationReport(BaseModel):
    run_id: uuid.UUID | None = None
    status: str
    can_seed_staging: bool
    can_promote_production: bool
    scopes: list[ScopeStagingVerificationReport]
    summary: dict[str, Any] = Field(default_factory=dict)
    created_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContentStagingReadinessService:
    def __init__(self, scope_registry: ContentScopeRegistry | None = None) -> None:
        self.scope_registry = scope_registry or ContentScopeRegistry()

    async def verify_all_scopes(
        self,
        session: AsyncSession,
        *,
        include_partial: bool = True,
        actor_id: str | None = None,
        persist: bool = True,
        include_review_scopes: bool = False,
    ) -> AllScopeStagingVerificationReport:
        # The expanded Content Factory registry contains many review/staging
        # scopes. The default all-scope staging gate is production-facing and
        # must remain limited to active learner-visible scopes unless a caller
        # explicitly opts into review-scope verification. This preserves the
        # Grade 4 beta boundary while keeping review scopes individually
        # addressable by scope_id.
        registry_scopes = (
            self.scope_registry.list_scopes()
            if include_review_scopes
            else self.scope_registry.list_active_scopes()
        )
        reports = [
            await self.verify_scope(scope.scope_id, session=session, include_partial=include_partial, actor_id=actor_id)
            for scope in registry_scopes
        ]
        report = AllScopeStagingVerificationReport(
            status="completed",
            can_seed_staging=any(scope.can_seed_staging for scope in reports),
            can_promote_production=all(scope.can_promote_production for scope in reports) if reports else False,
            scopes=reports,
            summary=self._all_scope_summary(reports),
            created_by=actor_id,
        )
        if persist:
            report = await self.persist_report(session, report, actor_id=actor_id)
        return report

    async def verify_scope(
        self,
        scope_id: str,
        *,
        session: AsyncSession,
        include_partial: bool = True,
        actor_id: str | None = None,
    ) -> ScopeStagingVerificationReport:
        try:
            targets = self.scope_registry.get_scope_targets(scope_id)
        except LookupError:
            return ScopeStagingVerificationReport(
                scope_id=scope_id,
                status=StagingReadinessStatus.BLOCKED_BY_MISSING_SCOPE,
                can_seed_staging=False,
                can_promote_production=False,
                blockers=[ScopeBlocker(code="missing_scope", message=f"Scope {scope_id} is not configured.")],
                summary={"actor_id": actor_id},
            )

        artifacts = await self._load_scope_artifacts(session, scope_id)
        source_index = await self._load_source_index(session, [artifact.artifact_id for artifact in artifacts])
        layers: list[LayerReadinessSummary] = []
        blockers: list[ScopeBlocker] = []

        for target in targets:
            for key, required in sorted(target.targets.items()):
                layer_name = key.rsplit(".", 1)[0]
                if int(required) <= 0:
                    layers.append(LayerReadinessSummary(layer=layer_name, caps_ref=target.caps_ref, target=int(required), status=StagingReadinessStatus.NOT_CONFIGURED))
                    continue
                matching = [
                    artifact
                    for artifact in artifacts
                    if _value(artifact.content_layer) == layer_name and artifact.caps_ref == target.caps_ref
                ]
                summary = self._layer_summary(layer_name, target.caps_ref, int(required), matching, source_index)
                layers.append(summary)
                blockers.extend(self._layer_blockers(summary))

        if not targets:
            blockers.append(ScopeBlocker(code="missing_targets", severity=BlockerSeverity.BLOCKING, message="Scope has no configured coverage targets."))

        status_value = self._scope_status(layers, blockers)
        stageable_total = sum(layer.stageable for layer in layers)
        pending_review_total = sum(layer.pending_review for layer in layers)
        can_seed = stageable_total > 0 if include_partial else status_value == StagingReadinessStatus.READY_FOR_STAGING
        can_promote = status_value == StagingReadinessStatus.READY_FOR_STAGING and pending_review_total == 0 and not blockers
        return ScopeStagingVerificationReport(
            scope_id=scope_id,
            status=status_value,
            can_seed_staging=can_seed,
            can_promote_production=can_promote,
            blockers=blockers,
            layers=layers,
            summary={
                "target": sum(layer.target for layer in layers),
                "approved": sum(layer.approved for layer in layers),
                "pending_review": pending_review_total,
                "generated": sum(layer.generated for layer in layers),
                "validation_failed": sum(layer.validation_failed for layer in layers),
                "rejected": sum(layer.rejected for layer in layers),
                "quarantined": sum(layer.quarantined for layer in layers),
                "stageable": stageable_total,
                "blockers": len(blockers),
            },
        )

    async def get_scope_blockers(self, scope_id: str, *, session: AsyncSession) -> list[ScopeBlocker]:
        return (await self.verify_scope(scope_id, session=session)).blockers

    async def persist_report(
        self,
        session: AsyncSession,
        report: AllScopeStagingVerificationReport,
        *,
        actor_id: str | None = None,
    ) -> AllScopeStagingVerificationReport:
        run_id = report.run_id or uuid.uuid4()
        stored = ContentStagingVerificationRun(
            run_id=run_id,
            status=report.status,
            summary_json=report.summary,
            created_by=actor_id,
            completed_at=datetime.now(timezone.utc),
        )
        session.add(stored)
        for scope_report in report.scopes:
            session.add(
                ContentStagingVerificationScopeResult(
                    run_id=run_id,
                    scope_id=scope_report.scope_id,
                    status=scope_report.status.value,
                    can_seed_staging=scope_report.can_seed_staging,
                    can_promote_production=scope_report.can_promote_production,
                    summary_json={**scope_report.summary, "layers": [layer.model_dump(mode="json") for layer in scope_report.layers]},
                    blockers_json=[blocker.model_dump(mode="json", exclude_none=True) for blocker in scope_report.blockers],
                    created_by=actor_id,
                    completed_at=datetime.now(timezone.utc),
                )
            )
        await session.flush()
        return report.model_copy(update={"run_id": run_id})

    async def list_runs(self, session: AsyncSession, *, limit: int = 20) -> list[ContentStagingVerificationRun]:
        result = await session.execute(select(ContentStagingVerificationRun).order_by(ContentStagingVerificationRun.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_run_report(self, session: AsyncSession, run_id: str | uuid.UUID) -> AllScopeStagingVerificationReport:
        run = await session.get(ContentStagingVerificationRun, uuid.UUID(str(run_id)))
        if run is None:
            raise LookupError(f"Staging verification run {run_id} not found.")
        result = await session.execute(
            select(ContentStagingVerificationScopeResult)
            .where(ContentStagingVerificationScopeResult.run_id == run.run_id)
            .order_by(ContentStagingVerificationScopeResult.scope_id)
        )
        scopes: list[ScopeStagingVerificationReport] = []
        for row in result.scalars().all():
            summary = row.summary_json or {}
            layers = [LayerReadinessSummary.model_validate(layer) for layer in summary.get("layers", [])]
            scopes.append(
                ScopeStagingVerificationReport(
                    scope_id=row.scope_id,
                    status=StagingReadinessStatus(row.status),
                    can_seed_staging=row.can_seed_staging,
                    can_promote_production=row.can_promote_production,
                    blockers=[ScopeBlocker.model_validate(blocker) for blocker in (row.blockers_json or [])],
                    layers=layers,
                    summary={key: value for key, value in summary.items() if key != "layers"},
                )
            )
        return AllScopeStagingVerificationReport(
            run_id=run.run_id,
            status=run.status,
            can_seed_staging=any(scope.can_seed_staging for scope in scopes),
            can_promote_production=all(scope.can_promote_production for scope in scopes) if scopes else False,
            scopes=scopes,
            summary=run.summary_json or {},
            created_by=run.created_by,
            created_at=run.created_at,
        )

    async def _load_scope_artifacts(self, session: AsyncSession, scope_id: str) -> list[ContentGenerationArtifact]:
        result = await session.execute(select(ContentGenerationArtifact).where(ContentGenerationArtifact.scope_id == scope_id))
        return list(result.scalars().all())

    async def _load_source_index(self, session: AsyncSession, artifact_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[ContentArtifactSource]]:
        if not artifact_ids:
            return {}
        result = await session.execute(select(ContentArtifactSource).where(ContentArtifactSource.artifact_id.in_(artifact_ids)))
        index: dict[uuid.UUID, list[ContentArtifactSource]] = defaultdict(list)
        for source in result.scalars().all():
            index[source.artifact_id].append(source)
        return index

    def _layer_summary(
        self,
        layer_name: str,
        caps_ref: str,
        target: int,
        artifacts: list[ContentGenerationArtifact],
        source_index: dict[uuid.UUID, list[ContentArtifactSource]],
    ) -> LayerReadinessSummary:
        counts = defaultdict(int)
        for artifact in artifacts:
            counts[_value(artifact.status)] += 1
        approved_artifacts = [artifact for artifact in artifacts if _value(artifact.status) in {ContentArtifactStatus.APPROVED.value, ContentArtifactStatus.SEEDED_STAGING.value, ContentArtifactStatus.PROMOTED_PRODUCTION.value}]
        invalid_provenance = sum(1 for artifact in approved_artifacts if not self._has_valid_provenance(artifact, source_index.get(artifact.artifact_id, [])))
        invalid_license = sum(1 for artifact in approved_artifacts if self._has_invalid_license(source_index.get(artifact.artifact_id, [])))
        low_source_quality = sum(1 for artifact in approved_artifacts if self._has_low_source_quality(source_index.get(artifact.artifact_id, [])))
        stageable = max(0, len(approved_artifacts) - invalid_provenance - invalid_license - low_source_quality)
        if target <= 0:
            status_value = StagingReadinessStatus.NOT_CONFIGURED
        elif stageable >= target:
            status_value = StagingReadinessStatus.READY_FOR_STAGING
        elif stageable > 0:
            status_value = StagingReadinessStatus.PARTIALLY_STAGEABLE
        elif counts[ContentArtifactStatus.PENDING_REVIEW.value] > 0:
            status_value = StagingReadinessStatus.BLOCKED_BY_REVIEW
        elif counts[ContentArtifactStatus.GENERATED.value] > 0 and counts[ContentArtifactStatus.VALIDATION_FAILED.value] > 0:
            status_value = StagingReadinessStatus.BLOCKED_BY_VALIDATION
        elif invalid_provenance > 0:
            status_value = StagingReadinessStatus.BLOCKED_BY_PROVENANCE
        else:
            status_value = StagingReadinessStatus.BLOCKED_BY_COVERAGE
        return LayerReadinessSummary(
            layer=layer_name,
            caps_ref=caps_ref,
            target=target,
            approved=len(approved_artifacts),
            pending_review=counts[ContentArtifactStatus.PENDING_REVIEW.value],
            generated=counts[ContentArtifactStatus.GENERATED.value],
            validation_failed=counts[ContentArtifactStatus.VALIDATION_FAILED.value],
            rejected=counts[ContentArtifactStatus.REJECTED.value],
            quarantined=counts[ContentArtifactStatus.QUARANTINED.value],
            seeded_staging=counts[ContentArtifactStatus.SEEDED_STAGING.value],
            promoted_production=counts[ContentArtifactStatus.PROMOTED_PRODUCTION.value],
            stageable=stageable,
            invalid_provenance=invalid_provenance,
            invalid_license=invalid_license,
            low_source_quality=low_source_quality,
            status=status_value,
        )

    def _layer_blockers(self, summary: LayerReadinessSummary) -> list[ScopeBlocker]:
        blockers: list[ScopeBlocker] = []
        common = {
            "layer": summary.layer,
            "caps_ref": summary.caps_ref,
            "required": summary.target,
            "approved": summary.stageable,
            "pending_review": summary.pending_review,
            "generated": summary.generated,
            "validation_failed": summary.validation_failed,
            "rejected": summary.rejected,
            "quarantined": summary.quarantined,
            "seeded_staging": summary.seeded_staging,
            "promoted_production": summary.promoted_production,
        }
        if summary.target <= 0:
            blockers.append(ScopeBlocker(code="target_not_configured", severity=BlockerSeverity.WARNING, **common))
        elif summary.stageable < summary.target:
            code = {
                StagingReadinessStatus.BLOCKED_BY_REVIEW: "pending_human_review",
                StagingReadinessStatus.BLOCKED_BY_VALIDATION: "validation_failed",
                StagingReadinessStatus.BLOCKED_BY_PROVENANCE: "invalid_provenance",
            }.get(summary.status, "insufficient_approved_coverage")
            blockers.append(ScopeBlocker(code=code, severity=BlockerSeverity.BLOCKING, **common))
        if summary.invalid_provenance:
            blockers.append(ScopeBlocker(code="invalid_provenance", severity=BlockerSeverity.BLOCKING, **common))
        if summary.invalid_license:
            blockers.append(ScopeBlocker(code="invalid_license", severity=BlockerSeverity.BLOCKING, **common))
        if summary.low_source_quality:
            blockers.append(ScopeBlocker(code="low_source_quality", severity=BlockerSeverity.BLOCKING, **common))
        return blockers

    def _scope_status(self, layers: list[LayerReadinessSummary], blockers: list[ScopeBlocker]) -> StagingReadinessStatus:
        configured = [layer for layer in layers if layer.target > 0]
        if not configured:
            return StagingReadinessStatus.NOT_CONFIGURED
        if all(layer.status == StagingReadinessStatus.READY_FOR_STAGING for layer in configured):
            return StagingReadinessStatus.READY_FOR_STAGING
        if any(layer.stageable > 0 for layer in configured):
            return StagingReadinessStatus.PARTIALLY_STAGEABLE
        for status_value in (
            StagingReadinessStatus.BLOCKED_BY_PROVENANCE,
            StagingReadinessStatus.BLOCKED_BY_LICENSE,
            StagingReadinessStatus.BLOCKED_BY_SOURCE_QUALITY,
            StagingReadinessStatus.BLOCKED_BY_VALIDATION,
            StagingReadinessStatus.BLOCKED_BY_REVIEW,
            StagingReadinessStatus.BLOCKED_BY_COVERAGE,
        ):
            if any(layer.status == status_value for layer in configured):
                return status_value
        return StagingReadinessStatus.BLOCKED_BY_COVERAGE if blockers else StagingReadinessStatus.NOT_CONFIGURED

    def _all_scope_summary(self, reports: list[ScopeStagingVerificationReport]) -> dict[str, Any]:
        return {
            "total_scopes": len(reports),
            "ready_scopes": sum(1 for scope in reports if scope.status == StagingReadinessStatus.READY_FOR_STAGING),
            "partially_stageable_scopes": sum(1 for scope in reports if scope.status == StagingReadinessStatus.PARTIALLY_STAGEABLE),
            "blocked_scopes": sum(1 for scope in reports if scope.status not in {StagingReadinessStatus.READY_FOR_STAGING, StagingReadinessStatus.PARTIALLY_STAGEABLE}),
            "blockers": sum(len(scope.blockers) for scope in reports),
        }

    def _has_valid_provenance(self, artifact: ContentGenerationArtifact, sources: list[ContentArtifactSource]) -> bool:
        if not artifact.source_snapshot_hash:
            return False
        if not sources:
            return False
        return all(bool(source.source_hash or source.source_document_id) for source in sources)

    def _has_invalid_license(self, sources: list[ContentArtifactSource]) -> bool:
        invalid = {"rejected", "unknown", "restricted", "unlicensed"}
        return any((source.license_status or "").lower() in invalid for source in sources)

    def _has_low_source_quality(self, sources: list[ContentArtifactSource]) -> bool:
        return any(source.source_quality_score is not None and float(source.source_quality_score) < 0.5 for source in sources)


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
