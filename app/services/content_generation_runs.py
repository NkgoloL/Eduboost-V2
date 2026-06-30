"""Durable Content Factory generation run/task ledger."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import ContentGenerationRun, ContentGenerationTask
from app.services.content_scope_registry import ContentScopeRegistry

TASK_STATES = {"queued", "running", "succeeded", "failed", "cancelled", "skipped"}


class ContentGenerationRunService:
    def __init__(self, scope_registry: ContentScopeRegistry | None = None) -> None:
        self.scope_registry = scope_registry or ContentScopeRegistry()

    async def create_run(self, session: AsyncSession, *, scope_id: str, layers: list[ContentLayer], requested_by: str, dry_run: bool = True, budget_cap: float | None = None, max_concurrency: int = 1) -> ContentGenerationRun:
        self.scope_registry.validate_scope_exists(scope_id)
        run = ContentGenerationRun(
            run_id=uuid.uuid4(),
            scope_id=scope_id,
            requested_by=requested_by,
            status="planned" if dry_run else "created",
            run_metadata={"layers": [layer.value for layer in layers], "dry_run": dry_run, "budget_cap": budget_cap, "max_concurrency": max_concurrency},
        )
        session.add(run)
        await session.flush()
        return run

    async def get_run(self, session: AsyncSession, run_id: uuid.UUID) -> ContentGenerationRun:
        run = await session.get(ContentGenerationRun, run_id)
        if run is None:
            raise LookupError(f"Generation run {run_id} not found.")
        return run

    async def list_runs(self, session: AsyncSession, *, scope_id: str | None = None, limit: int = 50) -> list[ContentGenerationRun]:
        stmt = select(ContentGenerationRun).order_by(ContentGenerationRun.created_at.desc()).limit(limit)
        if scope_id:
            stmt = stmt.where(ContentGenerationRun.scope_id == scope_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create_tasks_for_run(self, session: AsyncSession, run_id: uuid.UUID) -> list[ContentGenerationTask]:
        run = await self.get_run(session, run_id)
        layers = [ContentLayer(layer) for layer in run.run_metadata.get("layers", [])]
        existing = await self.get_run_tasks(session, run_id)
        if existing:
            return existing
        tasks: list[ContentGenerationTask] = []
        for caps_ref in self.scope_registry.get_scope_caps_refs(run.scope_id):
            for layer in layers:
                task = ContentGenerationTask(
                    task_id=uuid.uuid4(),
                    run_id=run.run_id,
                    scope_id=run.scope_id,
                    caps_ref=caps_ref,
                    content_layer=layer.value,
                    status="queued",
                    idempotency_key=f"{run.run_id}:{caps_ref}:{layer.value}:1",
                    admin_actor_id=run.requested_by,
                    task_metadata={"dry_run": bool(run.run_metadata.get("dry_run", True))},
                )
                session.add(task)
                tasks.append(task)
        await session.flush()
        return tasks

    async def get_run_tasks(self, session: AsyncSession, run_id: uuid.UUID) -> list[ContentGenerationTask]:
        result = await session.execute(select(ContentGenerationTask).where(ContentGenerationTask.run_id == run_id).order_by(ContentGenerationTask.caps_ref.asc(), ContentGenerationTask.content_layer.asc()))
        return list(result.scalars().all())

    async def mark_task_queued(self, session: AsyncSession, task_id: uuid.UUID) -> ContentGenerationTask:
        return await self._mark_task(session, task_id, "queued")

    async def mark_task_running(self, session: AsyncSession, task_id: uuid.UUID) -> ContentGenerationTask:
        task = await self._mark_task(session, task_id, "running")
        task.started_at = datetime.now(timezone.utc)
        await session.flush()
        return task

    async def mark_task_succeeded(self, session: AsyncSession, task_id: uuid.UUID, artifact_ids: list[str]) -> ContentGenerationTask:
        task = await self._mark_task(session, task_id, "succeeded")
        task.output_artifact_ids = artifact_ids
        task.finished_at = datetime.now(timezone.utc)
        await session.flush()
        return task

    async def mark_task_failed(self, session: AsyncSession, task_id: uuid.UUID, error: str) -> ContentGenerationTask:
        task = await self._mark_task(session, task_id, "failed")
        task.validation_failures = [error]
        task.finished_at = datetime.now(timezone.utc)
        await session.flush()
        return task

    async def cancel_run(self, session: AsyncSession, run_id: uuid.UUID, actor_id: str) -> ContentGenerationRun:
        run = await self.get_run(session, run_id)
        run.status = "cancelled"
        for task in await self.get_run_tasks(session, run_id):
            if task.status in {"queued", "running"}:
                task.status = "cancelled"
                task.admin_actor_id = actor_id
        await session.flush()
        return run

    async def retry_failed_tasks(self, session: AsyncSession, run_id: uuid.UUID, actor_id: str) -> list[ContentGenerationTask]:
        retry_tasks: list[ContentGenerationTask] = []
        for task in await self.get_run_tasks(session, run_id):
            if task.status != "failed" or task.attempt_number >= task.max_attempts:
                continue
            retry = ContentGenerationTask(
                task_id=uuid.uuid4(),
                run_id=task.run_id,
                scope_id=task.scope_id,
                caps_ref=task.caps_ref,
                content_layer=task.content_layer,
                status="queued",
                attempt_number=task.attempt_number + 1,
                max_attempts=task.max_attempts,
                idempotency_key=f"{task.run_id}:{task.caps_ref}:{_value(task.content_layer)}:{task.attempt_number + 1}",
                admin_actor_id=actor_id,
                task_metadata={"retry_of": str(task.task_id)},
            )
            session.add(retry)
            retry_tasks.append(retry)
        await session.flush()
        return retry_tasks

    async def _mark_task(self, session: AsyncSession, task_id: uuid.UUID, status: str) -> ContentGenerationTask:
        if status not in TASK_STATES:
            raise ValueError(f"Unsupported task status {status}.")
        task = await session.get(ContentGenerationTask, task_id)
        if task is None:
            raise LookupError(f"Generation task {task_id} not found.")
        task.status = status
        await session.flush()
        return task


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
