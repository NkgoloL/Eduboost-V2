"""Production promotion executor for Content Factory artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentProductionArtifact,
    ContentPromotionEvent,
    ContentStagingArtifact,
    ContentStagingSeedItem,
)
from app.services.content_production_promotion_gate import (
    ContentProductionPromotionGate,
)


@dataclass(frozen=True)
class ProductionPromotionPlan:
    scope_id: str
    layers: list[str]
    promotable_count: int
    skipped_count: int
    skipped: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ProductionPromotionResult:
    promotion_event_id: uuid.UUID
    scope_id: str
    status: str
    promoted_count: int
    skipped_count: int
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProductionPromotionPage:
    total: int
    limit: int
    offset: int
    items: list[ProductionPromotionResult] = field(default_factory=list)


@dataclass(frozen=True)
class ProductionRollbackResult:
    promotion_event_id: uuid.UUID
    status: str
    rolled_back_count: int


class ContentProductionPromotionExecutor:
    def __init__(
        self,
        gate: ContentProductionPromotionGate,
    ) -> None:
        self.gate = gate

    async def dry_run_promotion(
        self,
        session: AsyncSession,
        scope_id: str,
        *,
        layers: list[str] | None = None,
        actor_id: str,
    ) -> ProductionPromotionPlan:
        """Dry-run promotion produces a plan without mutation."""
        # Evaluate the gate first
        gate_report = await self.gate.evaluate_scope(session, scope_id, layers=layers)

        if gate_report.status.value != "promotable":
            raise ValueError(
                f"Cannot dry-run promotion: gate status is {gate_report.status.value}. "
                f"Blockers: {[b.message for b in gate_report.blockers]}"
            )

        # Find staged artifacts for the scope
        result = await session.execute(
            select(ContentStagingArtifact)
            .join(ContentStagingSeedItem, ContentStagingArtifact.artifact_id == ContentStagingSeedItem.artifact_id)
            .where(
                ContentStagingArtifact.scope_id == scope_id,
                ContentStagingArtifact.staging_status == "active",
                ContentStagingSeedItem.status == "seeded",
            )
        )

        staging_artifacts = result.scalars().all()

        return ProductionPromotionPlan(
            scope_id=scope_id,
            layers=layers or [],
            promotable_count=len(staging_artifacts),
            skipped_count=0,
        )

    async def promote_scope(
        self,
        session: AsyncSession,
        scope_id: str,
        *,
        layers: list[str] | None = None,
        actor_id: str,
        confirmation: str,
    ) -> ProductionPromotionResult:
        """Promote a scope to production."""
        # Verify confirmation
        expected_confirmation = f"PROMOTE {scope_id} TO PRODUCTION"
        if confirmation != expected_confirmation:
            raise ValueError(
                f"Confirmation mismatch. Expected: '{expected_confirmation}', Got: '{confirmation}'"
            )

        # Evaluate the gate
        gate_report = await self.gate.evaluate_scope(session, scope_id, layers=layers)

        if gate_report.status.value != "promotable":
            raise ValueError(
                f"Cannot promote: gate status is {gate_report.status.value}. "
                f"Blockers: {[b.message for b in gate_report.blockers]}"
            )

        # Create promotion event
        promotion_event_id = uuid.uuid4()
        promotion_event = ContentPromotionEvent(
            event_id=promotion_event_id,
            scope_id=scope_id,
            promoted_by=actor_id,
            status="in_progress",
            summary=gate_report.coverage_summary | gate_report.staging_summary,
        )
        session.add(promotion_event)
        await session.flush()

        # Find staged artifacts
        result = await session.execute(
            select(ContentStagingArtifact)
            .join(ContentStagingSeedItem, ContentStagingArtifact.artifact_id == ContentStagingSeedItem.artifact_id)
            .where(
                ContentStagingArtifact.scope_id == scope_id,
                ContentStagingArtifact.staging_status == "active",
                ContentStagingSeedItem.status == "seeded",
            )
        )

        staging_artifacts = result.scalars().all()
        promoted_count = 0
        errors = []

        # Promote each artifact
        for staging_artifact in staging_artifacts:
            try:
                # Check if production artifact already exists
                existing_result = await session.execute(
                    select(ContentProductionArtifact).where(
                        ContentProductionArtifact.artifact_id == staging_artifact.artifact_id,
                        ContentProductionArtifact.production_status == "active",
                    )
                )
                existing = existing_result.scalar_one_or_none()

                if existing:
                    # Mark existing as superseded
                    existing.production_status = "superseded"
                    existing.updated_at = datetime.now(timezone.utc)

                # Create new production artifact
                production_artifact = ContentProductionArtifact(
                    id=uuid.uuid4(),
                    artifact_id=staging_artifact.artifact_id,
                    staging_artifact_id=staging_artifact.id,
                    scope_id=staging_artifact.scope_id,
                    caps_ref=staging_artifact.caps_ref,
                    layer=staging_artifact.layer,
                    artifact_type=staging_artifact.artifact_type,
                    payload_json=staging_artifact.payload_json,
                    source_artifact_hash=staging_artifact.source_artifact_hash,
                    production_status="active",
                    created_by_promotion_event_id=promotion_event_id,
                )
                session.add(production_artifact)
                promoted_count += 1

            except Exception as e:
                errors.append(f"Failed to promote artifact {staging_artifact.artifact_id}: {str(e)}")

        # Update promotion event status
        if errors:
            promotion_event.status = "failed"
            promotion_event.summary = promotion_event.summary | {"errors": errors}
        else:
            promotion_event.status = "succeeded"
            promotion_event.summary = promotion_event.summary | {"promoted_count": promoted_count}

        promotion_event.updated_at = datetime.now(timezone.utc)
        await session.flush()

        return ProductionPromotionResult(
            promotion_event_id=promotion_event_id,
            scope_id=scope_id,
            status=promotion_event.status,
            promoted_count=promoted_count,
            skipped_count=0,
            errors=errors,
        )

    async def get_promotion_event(
        self,
        session: AsyncSession,
        promotion_event_id: str | uuid.UUID,
    ) -> ProductionPromotionResult:
        """Get a promotion event by ID."""
        event_uuid = uuid.UUID(str(promotion_event_id))

        result = await session.execute(
            select(ContentPromotionEvent).where(
                ContentPromotionEvent.event_id == event_uuid,
            )
        )
        event = result.scalar_one_or_none()

        if not event:
            raise ValueError(f"Promotion event {promotion_event_id} not found")

        # Count promoted artifacts
        count_result = await session.execute(
            select(func.count(ContentProductionArtifact.id)).where(
                ContentProductionArtifact.created_by_promotion_event_id == event_uuid,
            )
        )
        promoted_count = count_result.scalar() or 0

        return ProductionPromotionResult(
            promotion_event_id=event.event_id,
            scope_id=event.scope_id,
            status=event.status,
            promoted_count=promoted_count,
            skipped_count=0,
            errors=event.summary.get("errors", []),
        )

    async def list_promotion_events(
        self,
        session: AsyncSession,
        *,
        scope_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ProductionPromotionPage:
        """List promotion events."""
        query = select(ContentPromotionEvent)

        if scope_id:
            query = query.where(ContentPromotionEvent.scope_id == scope_id)

        query = query.order_by(ContentPromotionEvent.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        events = result.scalars().all()

        # Get total count
        count_query = select(func.count(ContentPromotionEvent.event_id))
        if scope_id:
            count_query = count_query.where(ContentPromotionEvent.scope_id == scope_id)

        count_result = await session.execute(count_query)
        total = count_result.scalar() or 0

        items = []
        for event in events:
            count_result = await session.execute(
                select(func.count(ContentProductionArtifact.id)).where(
                    ContentProductionArtifact.created_by_promotion_event_id == event.event_id,
                )
            )
            promoted_count = count_result.scalar() or 0

            items.append(
                ProductionPromotionResult(
                    promotion_event_id=event.event_id,
                    scope_id=event.scope_id,
                    status=event.status,
                    promoted_count=promoted_count,
                    skipped_count=0,
                    errors=event.summary.get("errors", []),
                )
            )

        return ProductionPromotionPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def rollback_promotion(
        self,
        session: AsyncSession,
        promotion_event_id: str | uuid.UUID,
        *,
        actor_id: str,
        reason: str,
    ) -> ProductionRollbackResult:
        """Rollback a promotion event."""
        event_uuid = uuid.UUID(str(promotion_event_id))

        # Find the promotion event
        result = await session.execute(
            select(ContentPromotionEvent).where(
                ContentPromotionEvent.event_id == event_uuid,
            )
        )
        event = result.scalar_one_or_none()

        if not event:
            raise ValueError(f"Promotion event {promotion_event_id} not found")

        # Find production artifacts created by this event
        artifacts_result = await session.execute(
            select(ContentProductionArtifact).where(
                ContentProductionArtifact.created_by_promotion_event_id == event_uuid,
                ContentProductionArtifact.production_status == "active",
            )
        )
        artifacts = artifacts_result.scalars().all()

        rolled_back_count = 0

        for artifact in artifacts:
            artifact.production_status = "rolled_back"
            artifact.updated_at = datetime.now(timezone.utc)
            rolled_back_count += 1

        # Update promotion event
        event.status = "rolled_back"
        event.summary = event.summary | {
            "rolled_back_by": actor_id,
            "rollback_reason": reason,
            "rolled_back_count": rolled_back_count,
            "rolled_back_at": datetime.now(timezone.utc).isoformat(),
        }
        event.updated_at = datetime.now(timezone.utc)

        await session.flush()

        return ProductionRollbackResult(
            promotion_event_id=event.event_id,
            status=event.status,
            rolled_back_count=rolled_back_count,
        )
