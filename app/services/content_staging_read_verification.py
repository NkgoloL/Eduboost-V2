"""Staging read verification for Content Factory artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentStagingArtifact,
    ContentStagingSeedItem,
)


@dataclass(frozen=True)
class StagingReadVerificationReport:
    seed_run_id: uuid.UUID
    passed: bool
    verified_count: int
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScopeStagingReadReport:
    scope_id: str
    passed: bool
    staged_artifacts_count: int
    errors: list[str] = field(default_factory=list)


class ContentStagingReadVerificationService:
    async def verify_seed_run(self, session: AsyncSession, seed_run_id: str | uuid.UUID, *, actor_id: str | None = None) -> StagingReadVerificationReport:
        run_uuid = uuid.UUID(str(seed_run_id))
        items = await session.execute(select(ContentStagingSeedItem).where(ContentStagingSeedItem.seed_run_id == run_uuid, ContentStagingSeedItem.status == "seeded"))

        seeded_items = items.scalars().all()
        errors = []
        verified_count = 0

        for item in seeded_items:
            # check staging row
            staging_row = await session.execute(
                select(ContentStagingArtifact).where(
                    ContentStagingArtifact.created_by_seed_run_id == run_uuid,
                    ContentStagingArtifact.artifact_id == item.artifact_id,
                )
            )
            matches = staging_row.scalars().all()

            if not matches:
                errors.append(f"Missing staging record for seeded artifact {item.artifact_id}")
                continue
            if len(matches) > 1:
                errors.append(f"Multiple staging records for seeded artifact {item.artifact_id}")
            artifact = matches[0]

            if artifact.staging_status != "active":
                errors.append(f"Staging record for {item.artifact_id} is not active ({artifact.staging_status})")
            if getattr(artifact, "scope_id", getattr(item, "scope_id", None)) != getattr(item, "scope_id", None):
                errors.append(f"Staging record for {item.artifact_id} has mismatched scope {artifact.scope_id}")
            if getattr(artifact, "caps_ref", getattr(item, "caps_ref", None)) != getattr(item, "caps_ref", None):
                errors.append(f"Staging record for {item.artifact_id} has mismatched caps_ref {artifact.caps_ref}")
            if getattr(artifact, "layer", getattr(item, "layer", None)) != getattr(item, "layer", None):
                errors.append(f"Staging record for {item.artifact_id} has mismatched layer {artifact.layer}")

            # check source artifact status
            source = await session.get(ContentGenerationArtifact, item.artifact_id)
            if not source:
                errors.append(f"Source artifact {item.artifact_id} deleted")
                continue

            source_status = source.status.value if hasattr(source.status, "value") else str(source.status)
            if source_status != ContentArtifactStatus.APPROVED.value:
                errors.append(f"Source artifact {item.artifact_id} status invalid for staging: {source_status}")

            verified_count += 1

        active_rows = await session.execute(
            select(ContentStagingArtifact).where(
                ContentStagingArtifact.created_by_seed_run_id == run_uuid,
                ContentStagingArtifact.staging_status == "active",
            )
        )
        active_count = len(active_rows.scalars().all())
        if active_count != len(seeded_items):
            errors.append(f"Seeded item count {len(seeded_items)} does not match active staging count {active_count}")

        return StagingReadVerificationReport(run_uuid, not bool(errors), verified_count, errors)

    async def verify_scope_staging(self, session: AsyncSession, scope_id: str, *, layers: list[str] | None = None) -> ScopeStagingReadReport:
        stmt = select(ContentStagingArtifact).where(ContentStagingArtifact.scope_id == scope_id, ContentStagingArtifact.staging_status == "active")
        if layers:
            stmt = stmt.where(ContentStagingArtifact.layer.in_(layers))

        result = await session.execute(stmt)
        artifacts = result.scalars().all()

        errors = []
        staged_count = 0

        for artifact in artifacts:
            source = await session.get(ContentGenerationArtifact, artifact.artifact_id)
            if not source:
                errors.append(f"Staged artifact {artifact.artifact_id} source missing")
                continue

            source_status = source.status.value if hasattr(source.status, "value") else str(source.status)

            if source_status in (ContentArtifactStatus.PENDING_REVIEW.value, ContentArtifactStatus.REJECTED.value, ContentArtifactStatus.QUARANTINED.value, ContentArtifactStatus.VALIDATION_FAILED.value):
                errors.append(f"Artifact {artifact.artifact_id} is in staging but status is {source_status}")

            staged_count += 1

        return ScopeStagingReadReport(scope_id, not bool(errors), staged_count, errors)
