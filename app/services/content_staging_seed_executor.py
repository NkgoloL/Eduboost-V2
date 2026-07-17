"""Staging seed executor for Content Factory artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentSeedRun,
    ContentStagingArtifact,
    ContentStagingSeedItem,
    ContentValidationReport,
)
from app.services.content_factory import ContentFactoryService


import asyncio
import logging
import os
import time
from sqlalchemy.exc import IntegrityError, OperationalError

logger = logging.getLogger(__name__)


async def _maybe_await(value: Any) -> Any:
    """Await coroutine-like values while accepting sync test doubles."""
    if hasattr(value, "__await__"):
        return await value
    return value


async def _session_flush(session: Any) -> None:
    operation = getattr(session, "flush", None)
    if operation is not None:
        await _maybe_await(operation())


async def _session_commit(session: Any) -> None:
    operation = getattr(session, "commit", None)
    if operation is not None:
        await _maybe_await(operation())


async def _session_rollback(session: Any) -> None:
    operation = getattr(session, "rollback", None)
    if operation is not None:
        await _maybe_await(operation())


class MissingForeignKeyError(Exception):
    """Raised when seeding fails due to a missing foreign key reference."""
    pass


@dataclass(frozen=True)
class SeedableArtifact:
    artifact_id: uuid.UUID
    scope_id: str
    caps_ref: str | None
    layer: str
    artifact_type: str
    payload_json: dict[str, Any]
    artifact_hash: str


@dataclass(frozen=True)
class SkippedArtifact:
    artifact_id: uuid.UUID
    reason: str


@dataclass(frozen=True)
class StagingSeedPlan:
    scope_id: str
    layers: list[str]
    seedable: list[SeedableArtifact]
    skipped: list[SkippedArtifact]


@dataclass(frozen=True)
class StagingSeedRunResult:
    seed_run_id: uuid.UUID
    scope_id: str
    status: str
    seeded_count: int
    skipped_count: int
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class StagingSeedItemResult:
    id: uuid.UUID
    seed_run_id: uuid.UUID
    artifact_id: uuid.UUID
    scope_id: str
    caps_ref: str | None
    layer: str
    artifact_type: str
    target_table: str
    target_record_id: str | None
    status: str
    skip_reason: str | None
    seed_payload_hash: str | None


@dataclass(frozen=True)
class StagingSeedRunPage:
    items: list[StagingSeedRunResult]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class StagingRollbackResult:
    seed_run_id: uuid.UUID
    status: str
    rolled_back_count: int


class ContentStagingSeedExecutor:
    def __init__(self, factory_service: ContentFactoryService | None = None) -> None:
        self.factory_service = factory_service or ContentFactoryService()

    async def dry_run_seed(self, session: AsyncSession, scope_id: str, *, layers: list[str] | None = None, actor_id: str | None = None) -> StagingSeedPlan:
        return await self._plan_seed(session, scope_id, layers=layers)

    async def seed_staging(self, session: AsyncSession, scope_id: str, *, layers: list[str] | None = None, actor_id: str, allow_partial: bool = True, batch_size: int | None = None) -> StagingSeedRunResult:
        plan = await self._plan_seed(session, scope_id, layers=layers)

        if not allow_partial and plan.skipped:
            return StagingSeedRunResult(
                seed_run_id=uuid.uuid4(),
                scope_id=scope_id,
                status="failed",
                seeded_count=0,
                skipped_count=len(plan.skipped),
                errors=["Partial seed disabled and artifacts were skipped. " + "; ".join({s.reason for s in plan.skipped})]
            )

        run_id = uuid.uuid4()
        summary = {
            "actor_id": actor_id,
            "layers": layers,
            "allow_partial": allow_partial,
            "planned_count": len(plan.seedable),
            "skipped_count": len(plan.skipped),
            "skipped_reasons": [{ "artifact_id": str(s.artifact_id), "reason": s.reason } for s in plan.skipped],
        }

        seeded_count = 0
        skipped_count_total = len(plan.skipped)
        errors = []
        status = "seeded_staging" if not plan.skipped and plan.seedable else "partially_seeded_staging" if plan.seedable else "failed"

        run = ContentSeedRun(
            seed_run_id=run_id,
            scope_id=scope_id,
            dry_run=False,
            status=status,
            summary=summary,
        )
        session.add(run)

        for skipped in plan.skipped:
            item = ContentStagingSeedItem(
                seed_run_id=run_id,
                artifact_id=skipped.artifact_id,
                scope_id=scope_id,
                caps_ref=None,
                layer="unknown",
                artifact_type="unknown",
                target_table="none",
                status="skipped",
                skip_reason=skipped.reason,
            )
            session.add(item)

        try:
            await _session_flush(session)
        except Exception:
            logger.exception(f"Unhandled exception during run init for scope {scope_id}")
            await _session_rollback(session)
            raise

        if batch_size is None:
            batch_size = int(os.environ.get("SEED_BATCH_SIZE", 500))

        seedable_list = plan.seedable
        total_seedable = len(seedable_list)

        for i in range(0, total_seedable, batch_size):
            batch = seedable_list[i : i + batch_size]
            batch_index = i // batch_size
            start_time = time.time()

            batch_artifact_ids = [artifact.artifact_id for artifact in batch]
            existing_stmt = select(ContentStagingArtifact).where(ContentStagingArtifact.artifact_id.in_(batch_artifact_ids))
            existing_res = await session.execute(existing_stmt)
            existing_map = {a.artifact_id: a for a in existing_res.scalars().all()}

            retries = 0
            while True:
                try:
                    for artifact in batch:
                        existing_staging = existing_map.get(artifact.artifact_id)
                        if existing_staging:
                            existing_staging.payload_json = artifact.payload_json
                            existing_staging.source_artifact_hash = artifact.artifact_hash
                            existing_staging.staging_status = "active"
                            existing_staging.created_by_seed_run_id = run_id
                            existing_staging.updated_at = datetime.now(timezone.utc)
                            staging_artifact_id = getattr(existing_staging, "id", uuid.uuid4())
                        else:
                            staging_artifact_id = uuid.uuid4()
                            staging_artifact = ContentStagingArtifact(
                                id=staging_artifact_id,
                                artifact_id=artifact.artifact_id,
                                scope_id=scope_id,
                                caps_ref=artifact.caps_ref,
                                layer=artifact.layer,
                                artifact_type=artifact.artifact_type,
                                payload_json=artifact.payload_json,
                                source_artifact_hash=artifact.artifact_hash,
                                staging_status="active",
                                created_by_seed_run_id=run_id,
                            )
                            session.add(staging_artifact)

                        item = ContentStagingSeedItem(
                            seed_run_id=run_id,
                            artifact_id=artifact.artifact_id,
                            scope_id=scope_id,
                            caps_ref=artifact.caps_ref,
                            layer=artifact.layer,
                            artifact_type=artifact.artifact_type,
                            target_table="content_staging_artifacts",
                            target_record_id=str(staging_artifact_id),
                            status="seeded",
                            rollback_payload_json={"staging_artifact_id": str(staging_artifact_id), "previous_staging_status": None},
                            seed_payload_hash=artifact.artifact_hash,
                        )
                        session.add(item)

                    await _session_commit(session)
                    elapsed = time.time() - start_time
                    seeded_count += len(batch)
                    logger.info(f"Seeded batch {batch_index} for scope {scope_id}: attempted={len(batch)}, upserted={len(batch)}, skipped=0, elapsed={elapsed:.3f}s")
                    break

                except IntegrityError as integrity_err:
                    await _session_rollback(session)
                    logger.warning(f"IntegrityError in batch commit for scope {scope_id}, retrying record-by-record: {integrity_err}")

                    for artifact in batch:
                        try:
                            existing_staging = existing_map.get(artifact.artifact_id)
                            if not existing_staging:
                                q = await session.execute(select(ContentStagingArtifact).where(ContentStagingArtifact.artifact_id == artifact.artifact_id))
                                existing_staging = q.scalar_one_or_none()

                            if existing_staging:
                                existing_staging.payload_json = artifact.payload_json
                                existing_staging.source_artifact_hash = artifact.artifact_hash
                                existing_staging.staging_status = "active"
                                existing_staging.created_by_seed_run_id = run_id
                                existing_staging.updated_at = datetime.now(timezone.utc)
                                staging_artifact_id = getattr(existing_staging, "id", uuid.uuid4())
                            else:
                                staging_artifact_id = uuid.uuid4()
                                staging_artifact = ContentStagingArtifact(
                                    id=staging_artifact_id,
                                    artifact_id=artifact.artifact_id,
                                    scope_id=scope_id,
                                    caps_ref=artifact.caps_ref,
                                    layer=artifact.layer,
                                    artifact_type=artifact.artifact_type,
                                    payload_json=artifact.payload_json,
                                    source_artifact_hash=artifact.artifact_hash,
                                    staging_status="active",
                                    created_by_seed_run_id=run_id,
                                )
                                session.add(staging_artifact)

                            item = ContentStagingSeedItem(
                                seed_run_id=run_id,
                                artifact_id=artifact.artifact_id,
                                scope_id=scope_id,
                                caps_ref=artifact.caps_ref,
                                layer=artifact.layer,
                                artifact_type=artifact.artifact_type,
                                target_table="content_staging_artifacts",
                                target_record_id=str(staging_artifact_id),
                                status="seeded",
                                rollback_payload_json={"staging_artifact_id": str(staging_artifact_id), "previous_staging_status": None},
                                seed_payload_hash=artifact.artifact_hash,
                            )
                            session.add(item)

                            await _session_commit(session)
                            seeded_count += 1

                        except IntegrityError as item_integrity_err:
                            await _session_rollback(session)
                            orig_msg = str(item_integrity_err.orig).lower() if item_integrity_err.orig else ""
                            if "foreign key" in orig_msg or (hasattr(item_integrity_err.orig, "pgcode") and item_integrity_err.orig.pgcode == "23503") or (hasattr(item_integrity_err.orig, "sqlstate") and item_integrity_err.orig.sqlstate == "23503"):
                                logger.error(f"Missing foreign key reference for scope {scope_id}, artifact {artifact.artifact_id}: {item_integrity_err}")
                                raise MissingForeignKeyError(f"Missing foreign key reference for artifact {artifact.artifact_id}") from item_integrity_err
                            else:
                                logger.warning(f"DB constraint violation for artifact {artifact.artifact_id}, skipping: {item_integrity_err}")
                                errors.append(f"Constraint violation for artifact {artifact.artifact_id}: {item_integrity_err}")
                                skipped_count_total += 1
                                try:
                                    item = ContentStagingSeedItem(
                                        seed_run_id=run_id,
                                        artifact_id=artifact.artifact_id,
                                        scope_id=scope_id,
                                        caps_ref=artifact.caps_ref,
                                        layer=artifact.layer,
                                        artifact_type=artifact.artifact_type,
                                        target_table="content_staging_artifacts",
                                        status="skipped",
                                        skip_reason=f"Constraint violation: {item_integrity_err}",
                                    )
                                    session.add(item)
                                    await _session_commit(session)
                                except Exception as log_err:
                                    await _session_rollback(session)
                                    logger.error(f"Failed to log skipped item: {log_err}")
                        except Exception as item_err:
                            await _session_rollback(session)
                            logger.exception(f"Unhandled exception on artifact {artifact.artifact_id}: {item_err}")
                            raise
                    break

                except (OperationalError, asyncio.TimeoutError) as timeout_err:
                    await _session_rollback(session)
                    retries += 1
                    if retries >= 3:
                        logger.error(f"Connection timeout / pool exhaustion after 3 attempts on batch {batch_index} for scope {scope_id}: {timeout_err}")
                        raise timeout_err
                    backoff = float(os.environ.get("SEED_RETRY_BACKOFF_BASE", 2.0)) ** retries
                    logger.warning(f"Connection timeout/pool exhaustion, retrying batch {batch_index} in {backoff}s (attempt {retries}/3)...")
                    await asyncio.sleep(backoff)

                except Exception as unhandled_err:
                    await _session_rollback(session)
                    logger.exception(f"Unhandled exception in batch commit for scope {scope_id}: {unhandled_err}")
                    raise

        return StagingSeedRunResult(
            seed_run_id=run_id,
            scope_id=scope_id,
            status=status,
            seeded_count=seeded_count,
            skipped_count=skipped_count_total,
            errors=errors,
        )

    async def get_seed_run(self, session: AsyncSession, seed_run_id: str | uuid.UUID) -> StagingSeedRunResult:
        run = await session.get(ContentSeedRun, uuid.UUID(str(seed_run_id)))
        if not run:
            raise LookupError(f"Seed run {seed_run_id} not found")

        seeded = run.summary.get("planned_count", 0)
        skipped = run.summary.get("skipped_count", 0)

        return StagingSeedRunResult(
            seed_run_id=run.seed_run_id,
            scope_id=run.scope_id,
            status=run.status,
            seeded_count=seeded,
            skipped_count=skipped,
        )

    async def list_seed_runs(self, session: AsyncSession, *, scope_id: str | None = None, limit: int = 50, offset: int = 0) -> StagingSeedRunPage:
        stmt = select(ContentSeedRun).where(ContentSeedRun.dry_run is False)
        if scope_id:
            stmt = stmt.where(ContentSeedRun.scope_id == scope_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(ContentSeedRun.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(stmt)

        items = []
        for run in result.scalars().all():
            items.append(StagingSeedRunResult(
                seed_run_id=run.seed_run_id,
                scope_id=run.scope_id,
                status=run.status,
                seeded_count=run.summary.get("planned_count", 0),
                skipped_count=run.summary.get("skipped_count", 0),
            ))

        return StagingSeedRunPage(items, int(total), limit, offset)

    async def list_seed_run_items(self, session: AsyncSession, seed_run_id: str | uuid.UUID) -> list[StagingSeedItemResult]:
        run_uuid = uuid.UUID(str(seed_run_id))
        result = await session.execute(
            select(ContentStagingSeedItem)
            .where(ContentStagingSeedItem.seed_run_id == run_uuid)
            .order_by(ContentStagingSeedItem.created_at.asc())
        )
        return [
            StagingSeedItemResult(
                id=item.id,
                seed_run_id=item.seed_run_id,
                artifact_id=item.artifact_id,
                scope_id=item.scope_id,
                caps_ref=item.caps_ref,
                layer=item.layer,
                artifact_type=item.artifact_type,
                target_table=item.target_table,
                target_record_id=item.target_record_id,
                status=item.status,
                skip_reason=item.skip_reason,
                seed_payload_hash=item.seed_payload_hash,
            )
            for item in result.scalars().all()
        ]

    async def rollback_seed_run(self, session: AsyncSession, seed_run_id: str | uuid.UUID, *, actor_id: str, reason: str) -> StagingRollbackResult:
        run = await session.get(ContentSeedRun, uuid.UUID(str(seed_run_id)))
        if not run:
            raise LookupError(f"Seed run {seed_run_id} not found")

        items = await session.execute(select(ContentStagingSeedItem).where(ContentStagingSeedItem.seed_run_id == run.seed_run_id, ContentStagingSeedItem.status == "seeded"))

        rolled_back = 0
        for item in items.scalars().all():
            item.status = "rolled_back"
            item.skip_reason = reason
            item.updated_at = datetime.now(timezone.utc)

            # Find associated staging artifact
            artifacts = await session.execute(select(ContentStagingArtifact).where(ContentStagingArtifact.created_by_seed_run_id == run.seed_run_id, ContentStagingArtifact.artifact_id == item.artifact_id))
            for a in artifacts.scalars().all():
                a.staging_status = "rolled_back"
                a.updated_at = datetime.now(timezone.utc)

            rolled_back += 1

        run.status = "rolled_back"
        run.summary = {
            **(run.summary or {}),
            "rollback_reason": reason,
            "rollback_actor": actor_id,
            "rolled_back_count": rolled_back,
        }

        await _session_flush(session)

        return StagingRollbackResult(
            seed_run_id=run.seed_run_id,
            status="rolled_back",
            rolled_back_count=rolled_back,
        )

    async def _plan_seed(self, session: AsyncSession, scope_id: str, layers: list[str] | None = None) -> StagingSeedPlan:
        stmt = select(ContentGenerationArtifact).where(ContentGenerationArtifact.scope_id == scope_id)
        result = await session.execute(stmt)
        artifacts = result.scalars().all()

        seedable = []
        skipped = []

        for artifact in artifacts:
            layer_val = artifact.content_layer.value if hasattr(artifact.content_layer, "value") else str(artifact.content_layer)

            if layers and layer_val not in layers:
                continue

            status_val = artifact.status.value if hasattr(artifact.status, "value") else str(artifact.status)

            if status_val == ContentArtifactStatus.PENDING_REVIEW.value:
                skipped.append(SkippedArtifact(artifact.artifact_id, "Artifact is pending review"))
                continue

            if status_val == ContentArtifactStatus.REJECTED.value:
                skipped.append(SkippedArtifact(artifact.artifact_id, "Artifact is rejected"))
                continue

            if status_val == ContentArtifactStatus.QUARANTINED.value:
                skipped.append(SkippedArtifact(artifact.artifact_id, "Artifact is quarantined"))
                continue

            if status_val == ContentArtifactStatus.VALIDATION_FAILED.value:
                skipped.append(SkippedArtifact(artifact.artifact_id, "Artifact validation failed"))
                continue

            if status_val != ContentArtifactStatus.APPROVED.value:
                skipped.append(SkippedArtifact(artifact.artifact_id, f"Artifact status {status_val} is not seedable"))
                continue

            # Verify valid provenance
            provenance = await self.factory_service.get_artifact_provenance(session, artifact.artifact_id)
            if not provenance.passed:
                skipped.append(SkippedArtifact(artifact.artifact_id, "Invalid provenance"))
                continue

            # Has latest validation passed?
            val_reports = await session.execute(select(ContentValidationReport).where(ContentValidationReport.artifact_id == artifact.artifact_id).order_by(ContentValidationReport.created_at.desc()).limit(1))
            val_report = val_reports.scalar_one_or_none()
            if val_report is None:
                skipped.append(SkippedArtifact(artifact.artifact_id, "Latest validation report missing"))
                continue
            if not val_report.passed:
                skipped.append(SkippedArtifact(artifact.artifact_id, "Latest validation failed"))
                continue

            seedable.append(SeedableArtifact(
                artifact_id=artifact.artifact_id,
                scope_id=artifact.scope_id,
                caps_ref=artifact.caps_ref,
                layer=layer_val,
                artifact_type=artifact.artifact_type.value if hasattr(artifact.artifact_type, "value") else str(artifact.artifact_type),
                payload_json=artifact.artifact_json,
                artifact_hash=artifact.artifact_hash or "",
            ))

        return StagingSeedPlan(scope_id, layers or [], seedable, skipped)
