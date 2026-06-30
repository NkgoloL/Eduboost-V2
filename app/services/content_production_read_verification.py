"""Production read verification for Content Factory artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentProductionArtifact,
    ContentPromotionEvent,
)


@dataclass(frozen=True)
class ProductionReadVerificationReport:
    promotion_event_id: uuid.UUID
    passed: bool
    verified_count: int
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScopeProductionReadReport:
    scope_id: str
    passed: bool
    production_artifacts_count: int
    errors: list[str] = field(default_factory=list)


class ContentProductionReadVerificationService:
    async def verify_promotion_event(
        self,
        session: AsyncSession,
        promotion_event_id: str | uuid.UUID,
        *,
        actor_id: str | None = None,
    ) -> ProductionReadVerificationReport:
        """Verify production records exist for promoted items."""
        event_uuid = uuid.UUID(str(promotion_event_id))

        # Find the promotion event
        result = await session.execute(
            select(ContentPromotionEvent).where(
                ContentPromotionEvent.event_id == event_uuid,
            )
        )
        event = result.scalar_one_or_none()

        if not event:
            return ProductionReadVerificationReport(
                promotion_event_id=event_uuid,
                passed=False,
                verified_count=0,
                errors=[f"Promotion event {promotion_event_id} not found"],
            )

        # Find production artifacts created by this event
        artifacts_result = await session.execute(
            select(ContentProductionArtifact).where(
                ContentProductionArtifact.created_by_promotion_event_id == event_uuid,
            )
        )
        production_artifacts = artifacts_result.scalars().all()

        errors = []
        verified_count = 0

        for prod_artifact in production_artifacts:
            # Check that production artifact is active
            if prod_artifact.production_status != "active":
                errors.append(
                    f"Production artifact {prod_artifact.artifact_id} status is {prod_artifact.production_status}, not active"
                )
                continue

            # Check that the source artifact is approved
            artifact_result = await session.execute(
                select(ContentGenerationArtifact).where(
                    ContentGenerationArtifact.artifact_id == prod_artifact.artifact_id,
                )
            )
            artifact = artifact_result.scalar_one_or_none()

            if not artifact:
                errors.append(f"Source artifact {prod_artifact.artifact_id} not found")
                continue

            if artifact.status != ContentArtifactStatus.APPROVED:
                errors.append(
                    f"Production artifact {prod_artifact.artifact_id} points to non-approved artifact (status: {artifact.status.value})"
                )
                continue

            verified_count += 1

        passed = len(errors) == 0

        return ProductionReadVerificationReport(
            promotion_event_id=event_uuid,
            passed=passed,
            verified_count=verified_count,
            errors=errors,
        )

    async def verify_scope_production(
        self,
        session: AsyncSession,
        scope_id: str,
        *,
        layers: list[str] | None = None,
    ) -> ScopeProductionReadReport:
        """Verify production records for a scope."""
        # Find active production artifacts for the scope
        result = await session.execute(
            select(ContentProductionArtifact).where(
                ContentProductionArtifact.scope_id == scope_id,
                ContentProductionArtifact.production_status == "active",
            )
        )
        production_artifacts = result.scalars().all()

        errors = []

        for prod_artifact in production_artifacts:
            # Check that the source artifact is approved
            artifact_result = await session.execute(
                select(ContentGenerationArtifact).where(
                    ContentGenerationArtifact.artifact_id == prod_artifact.artifact_id,
                )
            )
            artifact = artifact_result.scalar_one_or_none()

            if not artifact:
                errors.append(f"Source artifact {prod_artifact.artifact_id} not found")
                continue

            if artifact.status != ContentArtifactStatus.APPROVED:
                errors.append(
                    f"Production artifact {prod_artifact.artifact_id} points to non-approved artifact (status: {artifact.status.value})"
                )
                continue

        passed = len(errors) == 0

        return ScopeProductionReadReport(
            scope_id=scope_id,
            passed=passed,
            production_artifacts_count=len(production_artifacts),
            errors=errors,
        )
