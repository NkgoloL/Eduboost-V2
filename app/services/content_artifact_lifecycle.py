"""Centralized Content Factory artifact lifecycle transitions.

Phase 3 disables direct single-review approval. Approval is now derived from
append-only educator decisions in :mod:`content_review_governance`.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact
from app.services.content_factory import ContentFactoryService
from app.services.content_review_governance import ContentReviewGovernanceService


@dataclass(frozen=True)
class ArtifactStatusTransition:
    artifact_id: uuid.UUID
    previous_status: str
    new_status: str
    actor_id: str
    reason: str | None = None


class ContentArtifactLifecycleService:
    def __init__(
        self,
        factory_service: ContentFactoryService | None = None,
        governance_service: ContentReviewGovernanceService | None = None,
    ) -> None:
        self.factory_service = factory_service or ContentFactoryService()
        self.governance_service = governance_service or ContentReviewGovernanceService(
            factory_service=self.factory_service
        )

    async def create_artifact(
        self, session: AsyncSession, *, payload: dict[str, Any]
    ) -> ContentGenerationArtifact:
        return await self.factory_service.create_artifact(session, payload=payload)

    async def validate_for_review(self, session: AsyncSession, artifact_id: uuid.UUID):
        return await self.factory_service.validate_existing_artifact(session, artifact_id)

    async def submit_for_review(
        self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str
    ) -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        if previous not in {
            ContentArtifactStatus.GENERATED.value,
            ContentArtifactStatus.VALIDATION_FAILED.value,
            ContentArtifactStatus.REVISION_REQUIRED.value,
        }:
            raise ValueError(
                "Only generated, validation_failed, or revision_required artifacts can be submitted for review."
            )
        report = await self.validate_for_review(session, artifact_id)
        if not report.passed:
            artifact.status = ContentArtifactStatus.VALIDATION_FAILED
            raise ValueError("Artifact validation failed: " + "; ".join(report.errors))
        artifact.status = ContentArtifactStatus.PENDING_REVIEW
        artifact.approval_count = 0
        artifact.publication_eligible = False
        artifact.row_version = int(getattr(artifact, "row_version", 1) or 1) + 1
        await self.governance_service.record_external_transition(
            session,
            artifact=artifact,
            previous_status=previous,
            new_status=ContentArtifactStatus.PENDING_REVIEW.value,
            actor_id=actor_id,
            reason_code="submitted_for_review",
        )
        await session.flush()
        return ArtifactStatusTransition(
            artifact.artifact_id,
            previous,
            ContentArtifactStatus.PENDING_REVIEW.value,
            actor_id,
        )

    async def reject_artifact(
        self,
        session: AsyncSession,
        artifact_id: uuid.UUID,
        actor_id: str,
        reason: str,
    ) -> ArtifactStatusTransition:
        if not reason.strip():
            raise ValueError("Rejecting an artifact requires a reason.")
        return await self._set_status(
            session,
            artifact_id,
            actor_id,
            ContentArtifactStatus.REJECTED,
            reason,
            "legacy_reject",
        )

    async def quarantine_artifact(
        self,
        session: AsyncSession,
        artifact_id: uuid.UUID,
        actor_id: str,
        reason: str,
    ) -> ArtifactStatusTransition:
        current = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(current.status)
        artifact = await self.governance_service.quarantine_artifact(
            session,
            artifact_id=artifact_id,
            actor_id=actor_id,
            reason_code="manual_quarantine",
            reason=reason,
        )
        return ArtifactStatusTransition(
            artifact.artifact_id,
            previous,
            ContentArtifactStatus.QUARANTINED.value,
            actor_id,
            reason,
        )

    async def retire_artifact(
        self,
        session: AsyncSession,
        artifact_id: uuid.UUID,
        actor_id: str,
        reason: str,
    ) -> ArtifactStatusTransition:
        if not reason.strip():
            raise ValueError("Retiring an artifact requires a reason.")
        return await self._set_status(
            session,
            artifact_id,
            actor_id,
            ContentArtifactStatus.RETIRED,
            reason,
            "retired",
        )

    async def mark_seeded_staging(
        self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str
    ) -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        if previous != ContentArtifactStatus.APPROVED.value:
            raise ValueError("Only quorum-approved artifacts can be seeded to staging.")
        if not artifact.publication_eligible:
            raise ValueError("Artifact is not publication eligible.")
        artifact.status = ContentArtifactStatus.SEEDED_STAGING
        artifact.row_version = int(getattr(artifact, "row_version", 1) or 1) + 1
        await self.governance_service.record_external_transition(
            session,
            artifact=artifact,
            previous_status=previous,
            new_status=ContentArtifactStatus.SEEDED_STAGING.value,
            actor_id=actor_id,
            reason_code="seeded_staging",
        )
        await session.flush()
        return ArtifactStatusTransition(
            artifact.artifact_id,
            previous,
            ContentArtifactStatus.SEEDED_STAGING.value,
            actor_id,
        )

    async def mark_promoted_production(
        self, session: AsyncSession, artifact_id: uuid.UUID, actor_id: str
    ) -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        if previous != ContentArtifactStatus.SEEDED_STAGING.value:
            raise ValueError("Only seeded_staging artifacts can be promoted to production.")
        if not artifact.publication_eligible:
            raise ValueError("Artifact is not publication eligible.")
        artifact.status = ContentArtifactStatus.PROMOTED_PRODUCTION
        artifact.row_version = int(getattr(artifact, "row_version", 1) or 1) + 1
        await self.governance_service.record_external_transition(
            session,
            artifact=artifact,
            previous_status=previous,
            new_status=ContentArtifactStatus.PROMOTED_PRODUCTION.value,
            actor_id=actor_id,
            reason_code="promoted_production",
        )
        await session.flush()
        return ArtifactStatusTransition(
            artifact.artifact_id,
            previous,
            ContentArtifactStatus.PROMOTED_PRODUCTION.value,
            actor_id,
        )

    async def _set_status(
        self,
        session: AsyncSession,
        artifact_id: uuid.UUID,
        actor_id: str,
        status: ContentArtifactStatus,
        reason: str | None,
        reason_code: str,
    ) -> ArtifactStatusTransition:
        artifact = await self.factory_service.get_artifact(session, artifact_id)
        previous = _value(artifact.status)
        artifact.status = status
        artifact.publication_eligible = False
        artifact.row_version = int(getattr(artifact, "row_version", 1) or 1) + 1
        await self.governance_service.record_external_transition(
            session,
            artifact=artifact,
            previous_status=previous,
            new_status=status.value,
            actor_id=actor_id,
            reason_code=reason_code,
            reason=reason,
        )
        await session.flush()
        return ArtifactStatusTransition(
            artifact.artifact_id, previous, status.value, actor_id, reason
        )


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
