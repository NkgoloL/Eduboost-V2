"""Plan missing Content Factory generation tasks from readiness gaps."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import ContentGenerationRun, ContentGenerationTask
from app.services.content_generation.provider_factory import get_generation_settings
from app.services.content_generation.source_context import ContentGenerationSourceContextService
from app.services.content_scope_registry import ContentScopeRegistry
from app.services.content_staging_readiness import ContentStagingReadinessService

PLANNABLE_LAYERS = {
    ContentLayer.DIAGNOSTIC_ITEMS.value,
    ContentLayer.LESSONS.value,
    ContentLayer.ASSESSMENT_BLUEPRINTS.value,
    ContentLayer.STUDY_PLAN_TEMPLATES.value,
}
DEFAULT_PROMPT_VERSION = "cf-gen-v1"
DEFAULT_TARGET_VERSION = "1.0"
DEFAULT_GENERATOR_VERSION = "1.0"


@dataclass(frozen=True)
class GenerationPlanResult:
    run_id: uuid.UUID
    created_task_ids: list[uuid.UUID] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    missing: list[dict[str, Any]] = field(default_factory=list)


class ContentGenerationPlanner:
    def __init__(
        self,
        *,
        scope_registry: ContentScopeRegistry | None = None,
        readiness_service: ContentStagingReadinessService | None = None,
        source_context_service: ContentGenerationSourceContextService | None = None,
    ) -> None:
        self.scope_registry = scope_registry or ContentScopeRegistry()
        self.readiness_service = readiness_service or ContentStagingReadinessService(self.scope_registry)
        self.source_context_service = source_context_service or ContentGenerationSourceContextService()

    async def plan_missing_for_run(
        self,
        session: AsyncSession,
        run_id: uuid.UUID,
        *,
        actor_id: str | None = None,
        prompt_version: str = DEFAULT_PROMPT_VERSION,
        target_version: str = DEFAULT_TARGET_VERSION,
        generator_version: str = DEFAULT_GENERATOR_VERSION,
    ) -> GenerationPlanResult:
        run = await session.get(ContentGenerationRun, run_id)
        if run is None:
            raise LookupError(f"Generation run {run_id} not found.")
        scopes = self.scope_registry.list_scopes() if run.scope_id == "all_scopes" else [self.scope_registry.get_scope(run.scope_id)]
        created: list[uuid.UUID] = []
        skipped: list[dict[str, Any]] = []
        missing_rows: list[dict[str, Any]] = []
        max_artifacts_per_task = get_generation_settings().max_artifacts_per_task

        for scope in scopes:
            report = await self.readiness_service.verify_scope(scope.scope_id, session=session, include_partial=True)
            for layer in report.layers:
                if layer.layer not in PLANNABLE_LAYERS or layer.target <= 0:
                    continue
                missing_count = max(0, layer.target - layer.approved)
                if missing_count <= 0:
                    skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "coverage_green"})
                    continue
                context = await self.source_context_service.build_context(session, scope_id=scope.scope_id, caps_ref=layer.caps_ref)
                if not context.passed:
                    skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "missing_source_context", "errors": context.errors})
                    continue
                task_missing = min(missing_count, max_artifacts_per_task)
                idempotency_key = f"{scope.scope_id}:{layer.caps_ref}:{layer.layer}:{target_version}:{prompt_version}:{generator_version}"
                existing = await session.execute(select(ContentGenerationTask).where(ContentGenerationTask.idempotency_key == idempotency_key))
                existing_task = existing.scalar_one_or_none()
                if existing_task is not None:
                    skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "duplicate_task"})
                    continue
                task = ContentGenerationTask(
                    task_id=uuid.uuid4(),
                    run_id=run.run_id,
                    scope_id=scope.scope_id,
                    caps_ref=layer.caps_ref,
                    content_layer=layer.layer,
                    status="queued",
                    idempotency_key=idempotency_key,
                    provider=get_generation_settings().provider,
                    prompt_version=prompt_version,
                    admin_actor_id=actor_id,
                    task_metadata={
                        "target_version": target_version,
                        "prompt_version": prompt_version,
                        "generator_version": generator_version,
                        "required_count": layer.target,
                        "approved_count": layer.approved,
                        "missing_count": task_missing,
                        "topic_title": _topic_title(scope, layer.caps_ref),
                        "grade": scope.grade,
                        "subject_code": scope.subject_code,
                        "language": scope.language,
                    },
                )
                session.add(task)
                created.append(task.task_id)
                missing_rows.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "missing_count": task_missing})
        run.status = "planned"
        metadata = dict(run.run_metadata or {})
        metadata["planned_missing"] = missing_rows
        metadata["planning_skips"] = skipped
        run.run_metadata = metadata
        await session.flush()
        return GenerationPlanResult(run_id=run.run_id, created_task_ids=created, skipped=skipped, missing=missing_rows)


def _topic_title(scope: Any, caps_ref: str) -> str:
    for topic in getattr(scope, "topic_map", []) or []:
        if getattr(topic, "caps_ref", None) == caps_ref:
            return getattr(topic, "title", caps_ref)
    return caps_ref
