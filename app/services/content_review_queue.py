"""Review queue and evidence bundle service for Content Factory artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAssignment,
    ContentValidationReport,
)
from app.services.content_factory import ContentFactoryService
from app.services.content_review_risk import ContentReviewRiskService, ReviewRisk


@dataclass(frozen=True)
class ReviewQueueItem:
    artifact_id: uuid.UUID
    scope_id: str
    content_layer: str
    artifact_type: str
    caps_ref: str | None
    status: str
    risk_level: str
    risk_reasons: list[str]
    validation_status: str
    provenance_status: str
    reviewer_id: str | None = None
    created_at: Any | None = None


@dataclass(frozen=True)
class ReviewQueuePage:
    items: list[ReviewQueueItem]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class ReviewSummary:
    pending_review: int = 0
    low_risk: int = 0
    medium_risk: int = 0
    high_risk: int = 0
    critical_risk: int = 0
    assigned: int = 0


@dataclass(frozen=True)
class ArtifactReviewBundle:
    artifact: dict[str, Any]
    validation_report: dict[str, Any] | None
    provenance: dict[str, Any]
    sources: list[dict[str, Any]]
    review_risk: ReviewRisk
    generation_metadata: dict[str, Any]
    prior_review_events: list[dict[str, Any]] = field(default_factory=list)
    similar_artifacts: list[dict[str, Any]] = field(default_factory=list)


class ContentReviewQueueService:
    def __init__(self, risk_service: ContentReviewRiskService | None = None, factory_service: ContentFactoryService | None = None) -> None:
        self.risk_service = risk_service or ContentReviewRiskService()
        self.factory_service = factory_service or ContentFactoryService()

    async def list_queue(
        self,
        session: AsyncSession,
        *,
        scope_id: str | None = None,
        layer: str | None = None,
        caps_ref: str | None = None,
        artifact_type: str | None = None,
        risk_level: str | None = None,
        reviewer_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ReviewQueuePage:
        stmt = self._base_queue_stmt(scope_id=scope_id, layer=layer, caps_ref=caps_ref, artifact_type=artifact_type)
        stmt = stmt.order_by(ContentGenerationArtifact.created_at.asc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        artifacts = list(result.scalars().all())
        assignments = await self._load_assignments(session, [artifact.artifact_id for artifact in artifacts])
        validation = await self._latest_validation_reports(session, [artifact.artifact_id for artifact in artifacts])
        items: list[ReviewQueueItem] = []
        for artifact in artifacts:
            assignment = assignments.get(artifact.artifact_id)
            if reviewer_id and (assignment is None or assignment.assigned_to != reviewer_id):
                continue
            provenance = await self.factory_service.get_artifact_provenance(session, artifact.artifact_id)
            risk = self.risk_service.score_artifact(artifact, validation_report=validation.get(artifact.artifact_id), provenance_report=provenance)
            if risk_level and risk.level != risk_level:
                continue
            items.append(self._queue_item(artifact, risk, validation.get(artifact.artifact_id), provenance, assignment))
        count_result = await session.execute(select(func.count()).select_from(self._base_queue_stmt(scope_id=scope_id, layer=layer, caps_ref=caps_ref, artifact_type=artifact_type).subquery()))
        return ReviewQueuePage(items=items, total=int(count_result.scalar_one() or 0), limit=limit, offset=offset)

    async def get_review_summary(self, session: AsyncSession, scope_id: str | None = None) -> ReviewSummary:
        page = await self.list_queue(session, scope_id=scope_id, limit=500, offset=0)
        return ReviewSummary(
            pending_review=len(page.items),
            low_risk=sum(1 for item in page.items if item.risk_level == "low"),
            medium_risk=sum(1 for item in page.items if item.risk_level == "medium"),
            high_risk=sum(1 for item in page.items if item.risk_level == "high"),
            critical_risk=sum(1 for item in page.items if item.risk_level == "critical"),
            assigned=sum(1 for item in page.items if item.reviewer_id),
        )

    async def get_artifact_review_bundle(self, session: AsyncSession, artifact_id: str | uuid.UUID) -> ArtifactReviewBundle:
        artifact = await self.factory_service.get_artifact(session, uuid.UUID(str(artifact_id)))
        validation = (await self._latest_validation_reports(session, [artifact.artifact_id])).get(artifact.artifact_id)
        provenance = await self.factory_service.get_artifact_provenance(session, artifact.artifact_id)
        risk = self.risk_service.score_artifact(artifact, validation_report=validation, provenance_report=provenance)
        return ArtifactReviewBundle(
            artifact=_artifact_dict(artifact),
            validation_report=_validation_dict(validation) if validation else None,
            provenance={"passed": provenance.passed, "errors": provenance.errors, "source_snapshot_hash": provenance.source_snapshot_hash},
            sources=provenance.sources,
            review_risk=risk,
            generation_metadata={"provider": artifact.provider, "model": artifact.model, "prompt_version": artifact.prompt_version, "run_id": str(artifact.run_id) if artifact.run_id else None, "task_id": str(artifact.task_id) if artifact.task_id else None},
            prior_review_events=[_review_dict(review) for review in artifact.reviews],
            similar_artifacts=[],
        )

    def _base_queue_stmt(self, *, scope_id: str | None, layer: str | None, caps_ref: str | None, artifact_type: str | None):
        stmt = select(ContentGenerationArtifact).options(selectinload(ContentGenerationArtifact.sources), selectinload(ContentGenerationArtifact.reviews)).where(ContentGenerationArtifact.status == ContentArtifactStatus.PENDING_REVIEW)
        if scope_id:
            stmt = stmt.where(ContentGenerationArtifact.scope_id == scope_id)
        if layer:
            stmt = stmt.where(ContentGenerationArtifact.content_layer == layer)
        if caps_ref:
            stmt = stmt.where(ContentGenerationArtifact.caps_ref == caps_ref)
        if artifact_type:
            stmt = stmt.where(ContentGenerationArtifact.artifact_type == artifact_type)
        return stmt

    async def _load_assignments(self, session: AsyncSession, artifact_ids: list[uuid.UUID]) -> dict[uuid.UUID, ContentReviewAssignment]:
        if not artifact_ids:
            return {}
        result = await session.execute(select(ContentReviewAssignment).where(ContentReviewAssignment.artifact_id.in_(artifact_ids), ContentReviewAssignment.status.in_(["assigned", "in_review"])))
        return {assignment.artifact_id: assignment for assignment in result.scalars().all()}

    async def _latest_validation_reports(self, session: AsyncSession, artifact_ids: list[uuid.UUID]) -> dict[uuid.UUID, ContentValidationReport]:
        if not artifact_ids:
            return {}
        result = await session.execute(select(ContentValidationReport).where(ContentValidationReport.artifact_id.in_(artifact_ids)).order_by(ContentValidationReport.created_at.desc()))
        reports: dict[uuid.UUID, ContentValidationReport] = {}
        for report in result.scalars().all():
            reports.setdefault(report.artifact_id, report)
        return reports

    def _queue_item(self, artifact, risk, validation, provenance, assignment) -> ReviewQueueItem:
        return ReviewQueueItem(
            artifact_id=artifact.artifact_id,
            scope_id=artifact.scope_id,
            content_layer=_value(artifact.content_layer),
            artifact_type=_value(artifact.artifact_type),
            caps_ref=artifact.caps_ref,
            status=_value(artifact.status),
            risk_level=risk.level,
            risk_reasons=risk.reasons,
            validation_status="passed" if validation and validation.passed else "failed" if validation else "missing",
            provenance_status="passed" if provenance.passed else "failed",
            reviewer_id=assignment.assigned_to if assignment else None,
            created_at=artifact.created_at,
        )


def _artifact_dict(artifact) -> dict[str, Any]:
    return {"artifact_id": str(artifact.artifact_id), "scope_id": artifact.scope_id, "content_layer": _value(artifact.content_layer), "artifact_type": _value(artifact.artifact_type), "caps_ref": artifact.caps_ref, "status": _value(artifact.status), "artifact_json": artifact.artifact_json, "provider": artifact.provider}


def _validation_dict(report) -> dict[str, Any]:
    return {"validation_report_id": str(report.validation_report_id), "passed": report.passed, "checks": report.checks, "errors": report.errors}


def _review_dict(review) -> dict[str, Any]:
    return {"review_id": str(review.review_id), "review_action": _value(review.review_action), "review_reason": review.review_reason, "reviewer_id": review.reviewer_id}


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
