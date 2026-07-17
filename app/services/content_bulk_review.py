"""Guarded bulk review actions for Content Factory artifacts."""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.content_artifact_lifecycle import ContentArtifactLifecycleService
from app.services.content_factory import ContentFactoryService
from app.services.content_review_queue import ContentReviewQueueService
from app.services.content_review_risk import ContentReviewRiskService
from app.services.content_reviewer_assignment import ContentReviewerAssignmentService


@dataclass(frozen=True)
class BulkReviewResult:
    status: str
    artifact_ids: list[uuid.UUID] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)


class ContentBulkReviewService:
    def __init__(
        self,
        lifecycle_service: ContentArtifactLifecycleService | None = None,
        factory_service: ContentFactoryService | None = None,
        queue_service: ContentReviewQueueService | None = None,
        risk_service: ContentReviewRiskService | None = None,
        assignment_service: ContentReviewerAssignmentService | None = None,
    ) -> None:
        self.lifecycle_service = lifecycle_service or ContentArtifactLifecycleService()
        self.factory_service = factory_service or ContentFactoryService()
        self.queue_service = queue_service or ContentReviewQueueService()
        self.risk_service = risk_service or ContentReviewRiskService()
        self.assignment_service = assignment_service or ContentReviewerAssignmentService()

    async def bulk_approve(self, session: AsyncSession, artifact_ids: list[str | uuid.UUID], *, reviewer_id: str, notes: str) -> BulkReviewResult:
        del session, artifact_ids, reviewer_id, notes
        raise ValueError(
            "Bulk approval is disabled by Phase 3 governance. Each distinct reviewer must submit an attributable rubric decision for each artifact version."
        )

    async def bulk_reject(self, session: AsyncSession, artifact_ids: list[str | uuid.UUID], *, reviewer_id: str, reason: str) -> BulkReviewResult:
        max_batch = int(os.getenv("CONTENT_REVIEW_BULK_REJECT_MAX", "100"))
        if not reason or not reason.strip():
            raise ValueError("Bulk rejection requires a reason.")
        if len(artifact_ids) > max_batch:
            raise ValueError(f"Bulk rejection is limited to {max_batch} artifacts.")
        rejected = []
        for artifact_id in artifact_ids:
            rejected.append((await self.lifecycle_service.reject_artifact(session, uuid.UUID(str(artifact_id)), reviewer_id, reason)).artifact_id)
        return BulkReviewResult(status="rejected", artifact_ids=rejected, summary={"rejected": len(rejected)})

    async def bulk_quarantine(self, session: AsyncSession, artifact_ids: list[str | uuid.UUID], *, reviewer_id: str, reason: str) -> BulkReviewResult:
        if not reason or not reason.strip():
            raise ValueError("Bulk quarantine requires a reason.")
        quarantined = []
        for artifact_id in artifact_ids:
            quarantined.append((await self.lifecycle_service.quarantine_artifact(session, uuid.UUID(str(artifact_id)), reviewer_id, reason)).artifact_id)
        return BulkReviewResult(status="quarantined", artifact_ids=quarantined, summary={"quarantined": len(quarantined)})

    async def bulk_assign(self, session: AsyncSession, artifact_ids: list[str | uuid.UUID], *, reviewer_id: str, assigned_by: str, priority: str = "normal") -> BulkReviewResult:
        assignments = await self.assignment_service.assign_batch(session, artifact_ids, reviewer_id, assigned_by, priority=priority)
        return BulkReviewResult(status="assigned", artifact_ids=[assignment.artifact_id for assignment in assignments], summary={"assigned": len(assignments)})


def _value(value) -> str:
    return value.value if hasattr(value, "value") else str(value)
