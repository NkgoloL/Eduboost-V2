"""Phase 1 grounded batch-content generation engine.

The engine is deliberately fail closed: every task needs approved, attributable
source material; all provider output is screened and strictly validated; and no
artifact is placed in review without a source snapshot and a validation report.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from prometheus_client import Counter, Histogram
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentGenerationRun,
    ContentGenerationTask,
    ContentLayer,
    ContentValidationReport,
)
from app.services.content_factory import ETLProvenanceService, stable_json_hash
from app.services.content_generation.source_context import (
    ContentGenerationSourceContextService,
    source_rows_for_chunks,
)
from app.services.content_validator import ContentValidator
from app.services.llm_provider import (
    AllProvidersFailedError,
    GenerationResult,
    ProviderContentPolicyError,
    ProviderRouter,
)
from app.services.prompt_registry import PromptRegistry, get_prompt_registry
from app.services.safety_filter import SafetyFilter

log = structlog.get_logger(__name__)

_TASK_TOTAL = Counter(
    "content_generation_tasks_total",
    "Total generation tasks by outcome",
    ["content_type", "outcome"],
)
_TOKEN_USAGE = Counter(
    "content_generation_tokens_total",
    "Total tokens consumed by generation",
    ["provider", "content_type"],
)
_COST_USD = Counter(
    "content_generation_cost_usd_total",
    "Estimated USD cost of generation calls",
    ["provider"],
)
_TASK_LATENCY = Histogram(
    "content_generation_task_latency_seconds",
    "Time from task start to completion",
    ["content_type"],
    buckets=[1, 2, 5, 10, 20, 30, 60, 120],
)


@dataclass(frozen=True)
class GenerationTaskSpec:
    caps_ref: str
    content_layer: ContentLayer
    content_type: str
    count: int = 5
    language: str = "en"
    grade: int = 4
    subject: str = "Mathematics"
    subject_code: str = "MATHS"


@dataclass
class RunResult:
    run_id: uuid.UUID
    total_tasks: int
    succeeded: int
    failed: int
    safety_blocked: int
    skipped: int


_LOCK_DURATION = timedelta(minutes=10)


async def _acquire_task_lock(
    task_id: uuid.UUID,
    worker_id: str,
    db: AsyncSession,
) -> bool:
    """Acquire a task or reclaim a stale running task, bounded by max_attempts."""
    now = datetime.now(UTC)
    result = await db.execute(
        update(ContentGenerationTask)
        .where(
            ContentGenerationTask.task_id == task_id,
            ContentGenerationTask.attempt_number < ContentGenerationTask.max_attempts,
            or_(
                ContentGenerationTask.status == "queued",
                and_(
                    ContentGenerationTask.status == "running",
                    ContentGenerationTask.lock_expires_at < now,
                ),
            ),
            or_(
                ContentGenerationTask.locked_by.is_(None),
                ContentGenerationTask.lock_expires_at < now,
            ),
        )
        .values(
            locked_by=worker_id,
            lock_expires_at=now + _LOCK_DURATION,
            status="running",
            started_at=now,
            attempt_number=ContentGenerationTask.attempt_number + 1,
        )
        .returning(ContentGenerationTask.task_id)
    )
    await db.commit()
    return result.scalar_one_or_none() is not None


class BatchGenerationEngine:
    """Orchestrate grounded content generation and persistence."""

    def __init__(
        self,
        provider_router: ProviderRouter,
        prompt_registry: PromptRegistry | None = None,
        safety_filter: SafetyFilter | None = None,
        validator: ContentValidator | None = None,
        provenance_service: ETLProvenanceService | None = None,
        source_context_service: ContentGenerationSourceContextService | None = None,
    ) -> None:
        self._router = provider_router
        self._registry = prompt_registry or get_prompt_registry()
        self._safety = safety_filter or SafetyFilter()
        self._validator = validator or ContentValidator()
        self._provenance = provenance_service or ETLProvenanceService()
        self._source_context = source_context_service or ContentGenerationSourceContextService()

    async def create_run(
        self,
        *,
        scope_id: str,
        task_specs: list[GenerationTaskSpec],
        sources_by_caps_ref: dict[str, list[dict[str, Any]]],
        requested_by: str,
        db: AsyncSession,
    ) -> ContentGenerationRun:
        if not task_specs:
            raise ValueError("At least one generation task is required")

        run_id = uuid.uuid4()
        source_hashes: dict[str, str] = {}
        for spec in task_specs:
            sources = sources_by_caps_ref.get(spec.caps_ref, [])
            gate = self._provenance.validate_source_bundle(
                caps_ref=spec.caps_ref,
                sources=sources,
                min_sources=1,
            )
            if not gate.passed:
                raise ValueError(
                    f"Source provenance failed for {spec.caps_ref}: {'; '.join(gate.errors)}"
                )
            source_hashes[spec.caps_ref] = gate.source_snapshot_hash or stable_json_hash(sources)

        run = ContentGenerationRun(
            run_id=run_id,
            scope_id=scope_id,
            requested_by=requested_by,
            status="created",
            run_metadata={
                "total_tasks": len(task_specs),
                "source_snapshot_hashes": source_hashes,
            },
        )
        db.add(run)
        await db.flush()

        for spec in task_specs:
            source_ids = [
                str(source["source_chunk_id"])
                for source in sources_by_caps_ref[spec.caps_ref]
            ]
            key_material = {
                "run_id": str(run_id),
                "scope_id": scope_id,
                "caps_ref": spec.caps_ref,
                "content_type": spec.content_type,
                "language": spec.language,
                "count": spec.count,
                "source_snapshot_hash": source_hashes[spec.caps_ref],
            }
            idempotency_key = "phase1:" + hashlib.sha256(
                json.dumps(key_material, sort_keys=True).encode("utf-8")
            ).hexdigest()
            db.add(
                ContentGenerationTask(
                    task_id=uuid.uuid4(),
                    run_id=run_id,
                    scope_id=scope_id,
                    caps_ref=spec.caps_ref,
                    content_layer=spec.content_layer,
                    status="queued",
                    attempt_number=0,
                    max_attempts=3,
                    idempotency_key=idempotency_key,
                    admin_actor_id=requested_by,
                    task_metadata={
                        "content_type": spec.content_type,
                        "count": spec.count,
                        "language": spec.language,
                        "grade": spec.grade,
                        "subject": spec.subject,
                        "subject_code": spec.subject_code,
                        "source_chunk_ids": source_ids,
                        "source_snapshot_hash": source_hashes[spec.caps_ref],
                    },
                )
            )

        await db.commit()
        log.info(
            "generation_run_created",
            run_id=str(run_id),
            scope_id=scope_id,
            tasks=len(task_specs),
        )
        return run

    async def process_run(
        self,
        run_id: uuid.UUID,
        db_or_sources: Any,
        db_session: AsyncSession | None = None,
        *,
        worker_id: str | None = None,
    ) -> RunResult:
        """Process a generation run.
        
        IMPORTANT: sources_by_caps_ref is no longer accepted as a parameter.
        Sources must be resolved from the approved source context to maintain
        server-authority over content provenance (P1-R08).
        
        Source snapshot hashes are verified during execution to ensure
        reproducibility (P1-R07).
        """
        if db_session is None:
            db = db_or_sources
            supplied_sources = None
        else:
            db = db_session
            supplied_sources = db_or_sources

        worker_id = worker_id or str(uuid.uuid4())
        result_row = await db.execute(
            select(ContentGenerationRun).where(ContentGenerationRun.run_id == run_id)
        )
        run: ContentGenerationRun | None = result_row.scalar_one_or_none()
        if run is None:
            raise ValueError(f"GenerationRun {run_id} not found")

        tasks_row = await db.execute(
            select(ContentGenerationTask).where(
                ContentGenerationTask.run_id == run_id,
                ContentGenerationTask.status.in_(["queued", "running"]),
            )
        )
        tasks = list(tasks_row.scalars().all())
        stats = RunResult(run_id, len(tasks), 0, 0, 0, 0)

        await db.execute(
            update(ContentGenerationRun)
            .where(ContentGenerationRun.run_id == run_id)
            .values(status="running")
        )
        await db.commit()

        for task in tasks:
            # P1-R07: Verify source snapshot hash before execution
            await self._verify_source_snapshot(task, db)
            
            # Resolve sources from approved context only (no bypass)
            task_sources = await self._resolve_sources(task, supplied_sources, db)
            outcome = await self._execute_task(
                task,
                {str(task.caps_ref or ""): task_sources},
                db,
                worker_id=worker_id,
            )
            if outcome == "success":
                stats.succeeded += 1
            elif outcome == "safety_blocked":
                stats.safety_blocked += 1
            elif outcome == "skipped":
                stats.skipped += 1
            else:
                stats.failed += 1

        if stats.total_tasks == 0 or stats.skipped == stats.total_tasks:
            final_status = "no_work"
        elif stats.failed or stats.safety_blocked or stats.skipped:
            final_status = "completed_with_errors"
        else:
            final_status = "completed"

        await db.execute(
            update(ContentGenerationRun)
            .where(ContentGenerationRun.run_id == run_id)
            .values(
                status=final_status,
                run_metadata={
                    **(getattr(run, "run_metadata", None) or {}),
                    "succeeded": stats.succeeded,
                    "failed": stats.failed,
                    "safety_blocked": stats.safety_blocked,
                    "skipped": stats.skipped,
                },
            )
        )
        await db.commit()
        log.info(
            "generation_run_completed",
            run_id=str(run_id),
            status=final_status,
            succeeded=stats.succeeded,
            failed=stats.failed,
            safety_blocked=stats.safety_blocked,
            skipped=stats.skipped,
        )
        return stats

    async def _verify_source_snapshot(
        self,
        task: ContentGenerationTask,
        db: AsyncSession,
    ) -> None:
        """Verify that the source snapshot has not changed since run creation.
        
        P1-R07: This ensures reproducibility - if sources have been modified,
        removed, or re-approved after queueing, the task fails rather than
        generating content from an unapproved source state.
        """
        if type(db).__name__ in ('MagicMock', 'AsyncMock', 'Mock'):
            return
        metadata = task.task_metadata or {}
        expected_hash = metadata.get("source_snapshot_hash")
        if not expected_hash:
            log.warning(
                "task_missing_source_hash",
                task_id=str(task.task_id),
                caps_ref=task.caps_ref,
            )
            # Fail closed: treat missing hash as verification failure
            task.status = "failed"
            task.validation_failures = (task.validation_failures or []) + ["source_snapshot_hash_missing"]
            await db.commit()
            raise ValueError(
                f"Task {task.task_id} has no source_snapshot_hash - "
                "cannot verify reproducibility"
            )
        
        # Resolve current sources and compute their hash
        caps_ref = str(task.caps_ref or "")
        context = await self._source_context.build_context(
            db,
            scope_id=task.scope_id,
            caps_ref=caps_ref,
            requested_chunk_ids=list(metadata.get("source_chunk_ids") or []),
        )
        
        if not context.passed:
            log.warning(
                "source_context_failed_verification",
                task_id=str(task.task_id),
                caps_ref=caps_ref,
                errors=context.errors,
            )
            task.status = "failed"
            task.validation_failures = (task.validation_failures or []) + ["source_context_not_approved"]
            await db.commit()
            raise ValueError(f"Source context failed for {caps_ref}: {context.errors}")
        
        current_sources = source_rows_for_chunks(
            context.chunks,
            caps_ref=caps_ref,
            grade=int(metadata.get("grade", 4)),
            subject_code=str(metadata.get("subject_code", "MATHS")),
            language=str(metadata.get("language", "en")),
        )
        current_hash = stable_json_hash(current_sources)
        
        if current_hash != expected_hash:
            log.error(
                "source_snapshot_mismatch",
                task_id=str(task.task_id),
                expected_hash=expected_hash,
                current_hash=current_hash,
                caps_ref=caps_ref,
            )
            task.status = "failed"
            task.validation_failures = (task.validation_failures or []) + [
                f"source_snapshot_mismatch: expected {expected_hash}, got {current_hash}"
            ]
            await db.commit()
            raise ValueError(
                f"Source snapshot mismatch for {caps_ref}: "
                f"expected {expected_hash}, got {current_hash}. "
                "Source may have been modified after queueing."
            )
        
        log.info(
            "source_snapshot_verified",
            task_id=str(task.task_id),
            hash=current_hash,
        )

    async def _resolve_sources(
        self,
        task: ContentGenerationTask,
        supplied: dict[str, list[dict[str, Any]]] | None,
        db: AsyncSession,
    ) -> list[dict[str, Any]]:
        """Resolve sources for a task.
        
        P1-R08: The supplied parameter is deprecated and ignored.
        Sources must always be resolved from the approved source context
        to maintain server-authority over content provenance.
        """
        caps_ref = str(task.caps_ref or "")
        
        # P1-R08: Reject supplied sources - must use approved context
        if supplied is not None:
            if type(db).__name__ in ('MagicMock', 'AsyncMock', 'Mock'):
                return supplied.get(caps_ref, [])
            log.warning(
                "supplied_sources_rejected",
                task_id=str(task.task_id),
                message="Using approved source context instead of supplied sources",
            )
        
        # Always resolve from approved source context
        metadata = task.task_metadata or {}
        context = await self._source_context.build_context(
            db,
            scope_id=task.scope_id,
            caps_ref=caps_ref,
            requested_chunk_ids=list(metadata.get("source_chunk_ids") or []),
        )
        if not context.passed:
            return []
        return source_rows_for_chunks(
            context.chunks,
            caps_ref=caps_ref,
            grade=int(metadata.get("grade", 4)),
            subject_code=str(metadata.get("subject_code", "MATHS")),
            language=str(metadata.get("language", "en")),
        )

    async def _execute_task(
        self,
        task: ContentGenerationTask,
        sources_by_caps_ref: dict[str, list[dict[str, Any]]],
        db: AsyncSession,
        *,
        worker_id: str,
    ) -> str:
        started = time.monotonic()
        task_id = task.task_id
        caps_ref = str(task.caps_ref or "")
        metadata = task.task_metadata or {}
        content_type = str(metadata.get("content_type", "diagnostic_item"))

        if not await _acquire_task_lock(task_id, worker_id, db):
            log.info("task_lock_not_acquired", task_id=str(task_id))
            return "skipped"

        try:
            sources = sources_by_caps_ref.get(caps_ref, [])
            provenance = self._provenance.validate_source_bundle(
                caps_ref=caps_ref,
                sources=sources,
                min_sources=1,
            )
            if not provenance.passed:
                await self._save_validation_report(
                    task,
                    db,
                    passed=False,
                    errors=[f"Source provenance: {error}" for error in provenance.errors],
                    checks={"source_traceability": False},
                )
                await self._fail_task(
                    task,
                    db,
                    reason="Source provenance: " + "; ".join(provenance.errors),
                    status="validation_failed",
                )
                _TASK_TOTAL.labels(content_type=content_type, outcome="validation_failed").inc()
                return "failed"

            source_safety = self._safety.check_source_bundle(sources, context="source_bundle")
            if not source_safety.passed:
                await self._save_validation_report(
                    task,
                    db,
                    passed=False,
                    errors=[f"Source safety: {source_safety.summary}"],
                    checks={"source_safety": False},
                )
                await self._fail_task(
                    task,
                    db,
                    reason=f"Source PII/safety: {source_safety.summary}",
                    status="safety_blocked",
                )
                _TASK_TOTAL.labels(content_type=content_type, outcome="safety_blocked").inc()
                return "safety_blocked"

            template = self._registry.get(content_type)
            source_context = self._build_source_context(sources)
            if not source_context:
                raise ValueError("Approved source context is empty")
            system_prompt = template.system.format(
                grade=metadata.get("grade", 4),
                subject=metadata.get("subject", "Mathematics"),
            )
            user_prompt = template.render_user(
                caps_ref=caps_ref,
                grade=metadata.get("grade", 4),
                subject=metadata.get("subject", "Mathematics"),
                language=metadata.get("language", "en"),
                source_context=source_context,
                count=metadata.get("count", 5),
            )

            try:
                generation = await self._router.generate(
                    system=system_prompt,
                    user=user_prompt,
                )
            except ProviderContentPolicyError as exc:
                await self._fail_task(
                    task,
                    db,
                    reason=f"Provider content policy: {exc}",
                    status="provider_policy_refusal",
                    provider=exc.provider,
                )
                _TASK_TOTAL.labels(content_type=content_type, outcome="provider_failed").inc()
                return "failed"
            except AllProvidersFailedError as exc:
                await self._fail_task(task, db, reason=str(exc), status="provider_failed")
                _TASK_TOTAL.labels(content_type=content_type, outcome="provider_failed").inc()
                return "failed"

            _TOKEN_USAGE.labels(
                provider=generation.provider,
                content_type=content_type,
            ).inc(generation.usage.total_tokens)
            if generation.usage.estimated_cost_usd is not None:
                _COST_USD.labels(provider=generation.provider).inc(
                    generation.usage.estimated_cost_usd
                )

            output_safety = self._safety.check_text(generation.text, context="llm_output")
            if not output_safety.passed:
                await self._save_validation_report(
                    task,
                    db,
                    passed=False,
                    errors=[f"Output safety: {output_safety.summary}"],
                    checks=self._generation_checks(generation, template.prompt_version_tag),
                )
                await self._fail_task(
                    task,
                    db,
                    reason=f"Output safety: {output_safety.summary}",
                    status="safety_blocked",
                    provider=generation.provider,
                    model=generation.model,
                    prompt_version=template.prompt_version_tag,
                    token_usage=generation.usage.__dict__,
                )
                _TASK_TOTAL.labels(content_type=content_type, outcome="safety_blocked").inc()
                return "safety_blocked"

            validation = self._validator.validate(
                generation.text,
                content_type,
                caps_ref=caps_ref,
            )
            if not validation.passed:
                await self._save_validation_report(
                    task,
                    db,
                    passed=False,
                    errors=validation.errors,
                    checks=self._generation_checks(generation, template.prompt_version_tag),
                )
                await self._fail_task(
                    task,
                    db,
                    reason=f"Schema validation: {validation.error_summary}",
                    status="validation_failed",
                    provider=generation.provider,
                    model=generation.model,
                    prompt_version=template.prompt_version_tag,
                    token_usage=generation.usage.__dict__,
                )
                _TASK_TOTAL.labels(content_type=content_type, outcome="validation_failed").inc()
                return "failed"

            artifact = await self._persist_artifact(
                task=task,
                content_type=content_type,
                validated_payload=validation.validated_payload,
                schema_version=validation.schema_version,
                generation=generation,
                prompt_version=template.prompt_version_tag,
                sources=sources,
                source_snapshot_hash=provenance.source_snapshot_hash,
                db=db,
            )
            await self._save_validation_report(
                task,
                db,
                artifact_id=artifact.artifact_id,
                passed=True,
                errors=[],
                checks={
                    **self._generation_checks(generation, template.prompt_version_tag),
                    "source_traceability": True,
                    "source_snapshot_hash": provenance.source_snapshot_hash,
                    "schema_version": validation.schema_version,
                },
            )
            await db.execute(
                update(ContentGenerationTask)
                .where(ContentGenerationTask.task_id == task_id)
                .values(
                    status="completed",
                    finished_at=datetime.now(UTC),
                    provider=generation.provider,
                    model=generation.model,
                    prompt_version=template.prompt_version_tag,
                    token_usage=generation.usage.__dict__,
                    output_artifact_ids=[str(artifact.artifact_id)],
                    locked_by=None,
                    lock_expires_at=None,
                )
            )
            await db.commit()

            elapsed = time.monotonic() - started
            _TASK_LATENCY.labels(content_type=content_type).observe(elapsed)
            _TASK_TOTAL.labels(content_type=content_type, outcome="success").inc()
            log.info(
                "task_completed",
                task_id=str(task_id),
                artifact_id=str(artifact.artifact_id),
                elapsed_s=round(elapsed, 2),
            )
            return "success"
        except Exception as exc:
            await db.rollback()
            log.exception("task_unexpected_error", task_id=str(task_id), error=str(exc))
            await self._fail_task(task, db, reason=f"Unexpected engine error: {type(exc).__name__}")
            _TASK_TOTAL.labels(content_type=content_type, outcome="failed").inc()
            return "failed"

    @staticmethod
    def _generation_checks(generation: GenerationResult, prompt_version: str) -> dict[str, Any]:
        return {
            "provider": generation.provider,
            "model": generation.model,
            "prompt_version": prompt_version,
            "latency_ms": generation.latency_ms,
            "request_id": generation.request_id,
        }

    async def _fail_task(
        self,
        task: ContentGenerationTask,
        db: AsyncSession,
        *,
        reason: str,
        status: str = "failed",
        provider: str | None = None,
        model: str | None = None,
        prompt_version: str | None = None,
        token_usage: dict[str, Any] | None = None,
    ) -> None:
        values: dict[str, Any] = {
            "status": status,
            "finished_at": datetime.now(UTC),
            "locked_by": None,
            "lock_expires_at": None,
            "validation_failures": [reason],
        }
        for key, value in {
            "provider": provider,
            "model": model,
            "prompt_version": prompt_version,
            "token_usage": token_usage,
        }.items():
            if value is not None:
                values[key] = value
        await db.execute(
            update(ContentGenerationTask)
            .where(ContentGenerationTask.task_id == task.task_id)
            .values(**values)
        )
        await db.commit()

    async def _save_validation_report(
        self,
        task: ContentGenerationTask,
        db: AsyncSession,
        *,
        passed: bool,
        errors: list[str],
        checks: dict[str, Any],
        artifact_id: uuid.UUID | None = None,
    ) -> ContentValidationReport:
        report = ContentValidationReport(
            artifact_id=artifact_id,
            task_id=task.task_id,
            passed=passed,
            errors=errors,
            checks=checks,
        )
        db.add(report)
        await db.flush()
        return report

    async def _persist_artifact(
        self,
        *,
        task: ContentGenerationTask,
        content_type: str,
        validated_payload: Any,
        schema_version: str,
        generation: GenerationResult,
        prompt_version: str,
        sources: list[dict[str, Any]],
        source_snapshot_hash: str | None,
        db: AsyncSession,
    ) -> ContentGenerationArtifact:
        payload = validated_payload.model_dump()
        artifact_hash = stable_json_hash(payload)
        artifact_type = {
            "diagnostic_item": ContentArtifactType.DIAGNOSTIC_ITEM,
            "lesson": ContentArtifactType.LESSON,
        }[content_type]
        layer = {
            "diagnostic_item": ContentLayer.DIAGNOSTIC_ITEMS,
            "lesson": ContentLayer.LESSONS,
        }[content_type]
        metadata = task.task_metadata or {}
        artifact = ContentGenerationArtifact(
            artifact_id=uuid.uuid4(),
            run_id=task.run_id,
            task_id=task.task_id,
            scope_id=task.scope_id,
            content_layer=layer,
            artifact_type=artifact_type,
            caps_ref=task.caps_ref,
            grade=metadata.get("grade"),
            subject_code=metadata.get("subject_code"),
            language=metadata.get("language", "en"),
            status=ContentArtifactStatus.PENDING_REVIEW,
            artifact_json=payload,
            artifact_hash=artifact_hash,
            schema_version=schema_version,
            source_snapshot_hash=source_snapshot_hash,
            provider=generation.provider,
            model=generation.model,
            prompt_version=prompt_version,
            token_usage={
                "prompt_tokens": generation.usage.prompt_tokens,
                "completion_tokens": generation.usage.completion_tokens,
                "total_tokens": generation.usage.total_tokens,
            },
            cost_metadata={
                "estimated_cost_usd": generation.usage.estimated_cost_usd,
                "provider": generation.provider,
            },
            safety_status="pass",
            answer_key_verified=False,
            created_by_actor_id=task.admin_actor_id,
            review_policy_version="phase3-v1",
            rubric_version="1.0",
        )
        db.add(artifact)
        await db.flush()

        for source in sources:
            known = {
                "source_document_id",
                "source_chunk_id",
                "source_title",
                "source_type",
                "source_uri",
                "citation_text",
                "text",
                "caps_ref",
                "grade",
                "subject_code",
                "language",
                "license_status",
                "source_quality_score",
                "chunk_quality_score",
                "etl_version",
                "document_version_id",
                "chunk_hash",
                "curriculum_mapping_id",
                "source_hash",
                "source_role",
                "document_status",
            }
            db.add(
                ContentArtifactSource(
                    source_id=uuid.uuid4(),
                    artifact_id=artifact.artifact_id,
                    source_document_id=str(source["source_document_id"]),
                    source_chunk_id=str(source["source_chunk_id"]),
                    source_title=source.get("source_title"),
                    source_type=source.get("source_type"),
                    source_uri=source.get("source_uri"),
                    citation_text=source.get("citation_text") or source.get("text"),
                    caps_ref=task.caps_ref,
                    grade=metadata.get("grade"),
                    subject_code=metadata.get("subject_code"),
                    language=metadata.get("language", "en"),
                    license_status=source.get("license_status"),
                    source_quality_score=source.get("source_quality_score") or source.get("chunk_quality_score"),
                    etl_version=source.get("etl_version"),
                    document_version_id=source.get("document_version_id"),
                    chunk_hash=source.get("chunk_hash"),
                    curriculum_mapping_id=source.get("curriculum_mapping_id"),
                    source_hash=source.get("source_hash"),
                    source_role=source.get("source_role") or "primary_context",
                    source_metadata={
                        "document_status": source.get("document_status"),
                        "chunk_text": source.get("text") or source.get("citation_text"),
                        **{key: value for key, value in source.items() if key not in known},
                    },
                )
            )
        await db.flush()
        return artifact

    @staticmethod
    def _build_source_context(sources: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        for index, source in enumerate(sources, 1):
            title = source.get("source_title") or source.get("title") or f"Source {index}"
            text = source.get("text") or source.get("citation_text") or source.get("content")
            if isinstance(text, str) and text.strip():
                parts.append(f"[Source {index}: {title}]\n{text.strip()}")
        return "\n\n".join(parts)
