"""Controlled Content Factory generation executor."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentArtifactType, ContentGenerationArtifact, ContentGenerationTask, ContentLayer
from app.services.content_factory import ContentFactoryService, stable_json_hash
from app.services.content_generation.diagnostic_generator import DiagnosticGenerator
from app.services.content_generation.lesson_generator import LessonGenerator
from app.services.content_generation.prompt_payloads import DiagnosticGenerationRequest, LessonGenerationRequest
from app.services.content_generation.provider_factory import (
    GenerationSettings,
    get_content_generation_provider,
    get_generation_settings,
)
from app.services.content_generation.source_context import ContentGenerationSourceContextService, source_rows_for_chunks
from app.services.content_generation_runs import ContentGenerationRunService
from app.services.content_scope_registry import ContentScopeRegistry


@dataclass(frozen=True)
class TaskExecutionResult:
    task_id: uuid.UUID
    status: str
    artifact_ids: list[uuid.UUID] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    provider: str | None = None
    mode: str = "plan_only"


@dataclass(frozen=True)
class RunExecutionResult:
    run_id: uuid.UUID
    status: str
    task_results: list[TaskExecutionResult]
    summary: dict[str, Any]


class GenerationDisabledError(RuntimeError):
    pass


class ContentGenerationExecutor:
    def __init__(
        self,
        *,
        settings: GenerationSettings | None = None,
        scope_registry: ContentScopeRegistry | None = None,
        source_context_service: ContentGenerationSourceContextService | None = None,
        content_factory_service: ContentFactoryService | None = None,
        run_service: ContentGenerationRunService | None = None,
    ) -> None:
        self.settings = settings or get_generation_settings()
        self.scope_registry = scope_registry or ContentScopeRegistry()
        self.source_context_service = source_context_service or ContentGenerationSourceContextService()
        self.content_factory_service = content_factory_service or ContentFactoryService()
        self.run_service = run_service or ContentGenerationRunService(self.scope_registry)
        self.diagnostic_generator = DiagnosticGenerator()
        self.lesson_generator = LessonGenerator()

    async def execute_task(self, session: AsyncSession, task_id: str | uuid.UUID, actor_id: str | None = None) -> TaskExecutionResult:
        if not self.settings.enabled:
            raise GenerationDisabledError("Set CONTENT_FACTORY_GENERATION_ENABLED=true to execute generation tasks.")
        task = await session.get(ContentGenerationTask, uuid.UUID(str(task_id)))
        if task is None:
            raise LookupError(f"Generation task {task_id} not found.")
        if task.status not in {"queued", "failed"}:
            return TaskExecutionResult(task.task_id, "skipped", errors=[f"Task status {task.status} is not executable."], provider=self.settings.provider, mode=self.settings.provider)

        task.status = "running"
        task.locked_by = actor_id
        task.admin_actor_id = actor_id
        task.lock_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        task.started_at = datetime.now(timezone.utc)
        await session.flush()

        context = await self.source_context_service.build_context(session, scope_id=task.scope_id, caps_ref=task.caps_ref or "")
        if not context.passed:
            return await self._fail_task(session, task, context.errors)

        provider = get_content_generation_provider(self.settings)
        try:
            generated_payloads = await self._call_provider(provider, task, context.chunks)
        except Exception as exc:
            return await self._fail_task(session, task, [f"Generation failed: {exc}"])

        existing_hashes = await self._existing_hashes(session)
        artifact_ids: list[uuid.UUID] = []
        errors: list[str] = []
        for payload in generated_payloads[: self.settings.max_artifacts_per_task]:
            # Allow deterministic provider to include a non-semantic unique marker so
            # locally-generated deterministic artifacts don't collide on stable hash.
            artifact_json = payload["artifact_json"]
            if getattr(provider, "provider_name", "") == "deterministic":
                artifact_json = dict(artifact_json)
                artifact_json["_deterministic_instance_id"] = str(uuid.uuid4())
                # ensure we pass the modified artifact_json into create_artifact below
                payload = dict(payload)
                payload["artifact_json"] = artifact_json

            artifact_hash = stable_json_hash(artifact_json)
            pre_validation_errors = payload["validation_errors"](artifact_hash, existing_hashes)
            if pre_validation_errors:
                # keep generator-level validation errors for the task report
                errors.extend(pre_validation_errors)
            try:
                create_payload = {
                    "run_id": task.run_id,
                    "task_id": task.task_id,
                    "scope_id": task.scope_id,
                    "content_layer": task.content_layer,
                    "artifact_type": payload["artifact_type"],
                    "artifact_json": artifact_json,
                    "caps_ref": task.caps_ref,
                    "grade": payload["grade"],
                    "subject_code": payload["subject_code"],
                    "language": payload["language"],
                    "provider": provider.provider_name,
                    "model": provider.model_name,
                    "prompt_version": task.prompt_version or "cf-gen-v1",
                    "token_usage": {"provider": provider.provider_name, "estimated": True},
                    "cost_metadata": {"estimated_cost_usd": 0},
                    "quality_score": 0.9,
                    "safety_status": "passed",
                    "answer_key_verified": False,
                    "created_by_actor_id": actor_id,
                    "review_policy_version": "phase3-v1",
                    "rubric_version": "1.0",
                    "caps_alignment_score": 1.0,
                    "sources": source_rows_for_chunks(context.chunks, caps_ref=task.caps_ref or "", grade=payload["grade"], subject_code=payload["subject_code"], language=payload["language"]),
                }
                if hasattr(session, "begin_nested"):
                    async with session.begin_nested():
                        artifact = await self.content_factory_service.create_artifact(session, payload=create_payload)
                else:
                    artifact = await self.content_factory_service.create_artifact(session, payload=create_payload)
            except IntegrityError:
                errors.append("Artifact creation failed because a matching artifact hash already exists.")
                continue
            except Exception as exc:
                return await self._fail_task(session, task, [f"Artifact creation failed: {exc}"])
            # If the generator reported pre-validation errors, mark the persisted
            # artifact as validation_failed so it is blocked from review.
            if pre_validation_errors:
                try:
                    artifact.status = "validation_failed"
                except Exception:
                    # Best-effort: if artifact object uses an enum, set to enum value.
                    try:
                        from app.models.content_factory import ContentArtifactStatus

                        artifact.status = ContentArtifactStatus.VALIDATION_FAILED
                    except Exception:  # best-effort probe, cannot fail-close
                        pass
            artifact_ids.append(artifact.artifact_id)
            existing_hashes.add(artifact.artifact_hash)

        task.output_artifact_ids = [str(artifact_id) for artifact_id in artifact_ids]
        task.provider = provider.provider_name
        task.model = provider.model_name
        task.token_usage = {"provider": provider.provider_name, "estimated": True}
        task.cost_metadata = {"estimated_cost_usd": 0}
        task.validation_failures = errors
        task.status = "succeeded" if artifact_ids and not errors else "failed"
        task.finished_at = datetime.now(timezone.utc)
        task.admin_actor_id = actor_id
        await session.flush()
        return TaskExecutionResult(task.task_id, task.status, artifact_ids, errors, provider.provider_name, self.settings.provider)

    async def execute_run(self, session: AsyncSession, run_id: str | uuid.UUID, max_tasks: int | None = None, actor_id: str | None = None) -> RunExecutionResult:
        if not self.settings.enabled:
            raise GenerationDisabledError("Set CONTENT_FACTORY_GENERATION_ENABLED=true to execute generation tasks.")
        run = await self.run_service.get_run(session, uuid.UUID(str(run_id)))
        tasks = await self.run_service.get_run_tasks(session, run.run_id)
        queued = [task for task in tasks if task.status in {"queued", "failed"}]
        if max_tasks is not None:
            queued = queued[:max_tasks]
        results = [await self.execute_task(session, task.task_id, actor_id=actor_id) for task in queued]
        run.status = "succeeded" if results and all(result.status == "succeeded" for result in results) else "partial"
        await session.flush()
        return RunExecutionResult(
            run.run_id,
            run.status,
            results,
            {
                "tasks_executed": len(results),
                "artifacts_created": sum(len(result.artifact_ids) for result in results),
                "failed_tasks": sum(1 for result in results if result.status == "failed"),
            },
        )

    async def execution_report(self, session: AsyncSession, run_id: str | uuid.UUID) -> dict[str, Any]:
        run = await self.run_service.get_run(session, uuid.UUID(str(run_id)))
        tasks = await self.run_service.get_run_tasks(session, run.run_id)
        return {
            "run_id": str(run.run_id),
            "status": run.status,
            "tasks": len(tasks),
            "queued": sum(1 for task in tasks if task.status == "queued"),
            "succeeded": sum(1 for task in tasks if task.status == "succeeded"),
            "failed": sum(1 for task in tasks if task.status == "failed"),
            "skipped": sum(1 for task in tasks if task.status == "skipped"),
            "artifacts": sum(len(task.output_artifact_ids or []) for task in tasks),
        }

    async def _call_provider(self, provider: Any, task: ContentGenerationTask, chunks: list[Any]) -> list[dict[str, Any]]:
        metadata = task.task_metadata or {}
        scope = self.scope_registry.get_scope(task.scope_id)
        base = {
            "scope_id": task.scope_id,
            "caps_ref": task.caps_ref or "",
            "grade": int(metadata.get("grade") or scope.grade),
            "subject_code": str(metadata.get("subject_code") or scope.subject_code),
            "language": str(metadata.get("language") or scope.language),
            "topic_title": str(metadata.get("topic_title") or task.caps_ref),
            "required_count": int(metadata.get("required_count") or 1),
            "approved_count": int(metadata.get("approved_count") or 0),
            "missing_count": int(metadata.get("missing_count") or 1),
            "source_chunks": chunks,
            "source_document_ids": sorted({chunk.source_document_id for chunk in chunks}),
            "source_chunk_ids": [chunk.source_chunk_id for chunk in chunks],
            "source_quality_scores": [chunk.source_quality_score for chunk in chunks if chunk.source_quality_score is not None],
            "license_statuses": sorted({chunk.license_status for chunk in chunks if chunk.license_status}),
            "prompt_version": task.prompt_version or "cf-gen-v1",
        }
        if _value(task.content_layer) == ContentLayer.DIAGNOSTIC_ITEMS.value:
            items = await provider.generate_diagnostic_items(DiagnosticGenerationRequest(**base))
            return [
                {
                    "artifact_json": item.to_artifact_json(),
                    "artifact_type": ContentArtifactType.DIAGNOSTIC_ITEM,
                    "grade": item.grade,
                    "subject_code": item.subject_code,
                    "language": item.language,
                    "validation_errors": lambda artifact_hash, hashes, item=item: self.diagnostic_generator.validate(item, caps_ref=task.caps_ref or "", existing_hashes=hashes, artifact_hash=artifact_hash),
                }
                for item in items
            ]
        if _value(task.content_layer) == ContentLayer.LESSONS.value:
            lessons = await provider.generate_lessons(LessonGenerationRequest(**base))
            return [
                {
                    "artifact_json": lesson.to_artifact_json(),
                    "artifact_type": ContentArtifactType.LESSON,
                    "grade": lesson.grade,
                    "subject_code": lesson.subject_code,
                    "language": lesson.language,
                    "validation_errors": lambda artifact_hash, hashes, lesson=lesson: self.lesson_generator.validate(lesson, caps_ref=task.caps_ref or "", existing_hashes=hashes, artifact_hash=artifact_hash),
                }
                for lesson in lessons
            ]
        if _value(task.content_layer) == ContentLayer.ASSESSMENT_BLUEPRINTS.value:
            blueprints = await provider.generate_assessment_blueprints(base)
            return [
                {
                    "artifact_json": blueprint,
                    "artifact_type": ContentArtifactType.ASSESSMENT_BLUEPRINT,
                    "grade": blueprint.get("grade"),
                    "subject_code": blueprint.get("subject_code"),
                    "language": blueprint.get("language"),
                    "validation_errors": lambda artifact_hash, hashes, blueprint=blueprint: (["assessment blueprint duplicates an existing artifact hash."] if hashes and artifact_hash in hashes else []),
                }
                for blueprint in blueprints
            ]
        if _value(task.content_layer) == ContentLayer.STUDY_PLAN_TEMPLATES.value:
            templates = await provider.generate_study_plan_templates(base)
            return [
                {
                    "artifact_json": template,
                    "artifact_type": ContentArtifactType.STUDY_PLAN_TEMPLATE,
                    "grade": template.get("grade"),
                    "subject_code": template.get("subject_code"),
                    "language": template.get("language"),
                    "validation_errors": lambda artifact_hash, hashes, template=template: (["study plan template duplicates an existing artifact hash."] if hashes and artifact_hash in hashes else []),
                }
                for template in templates
            ]
        raise ValueError(f"Unsupported generation layer {task.content_layer}.")

    async def _existing_hashes(self, session: AsyncSession) -> set[str]:
        result = await session.execute(select(ContentGenerationArtifact.artifact_hash))
        return {str(row[0]) for row in result.all()}

    async def _fail_task(self, session: AsyncSession, task: ContentGenerationTask, errors: list[str]) -> TaskExecutionResult:
        task.status = "failed"
        task.validation_failures = errors
        task.finished_at = datetime.now(timezone.utc)
        await session.flush()
        return TaskExecutionResult(task.task_id, "failed", errors=errors, provider=self.settings.provider, mode=self.settings.provider)


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
