"""Comprehensive unit tests for ContentGenerationRunService and task states."""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import ContentGenerationRun, ContentGenerationTask
from app.services.content_generation_runs import (
    TASK_STATES,
    ContentGenerationRunService,
)


class TestContentGenerationRunModels:
    def test_task_states_constant(self):
        assert "queued" in TASK_STATES
        assert "running" in TASK_STATES
        assert "succeeded" in TASK_STATES
        assert "failed" in TASK_STATES
        assert "cancelled" in TASK_STATES
        assert "skipped" in TASK_STATES

    def test_generation_run_service_init(self):
        mock_registry = MagicMock()
        service = ContentGenerationRunService(scope_registry=mock_registry)
        assert service.scope_registry == mock_registry


class TestContentGenerationRunExecution:
    @pytest.mark.asyncio
    async def test_create_and_get_run(self):
        mock_registry = MagicMock()
        service = ContentGenerationRunService(scope_registry=mock_registry)
        session = AsyncMock()

        # 1. Create run
        run = await service.create_run(
            session,
            scope_id="grade4_maths",
            layers=[ContentLayer.LESSONS],
            requested_by="admin",
            dry_run=True,
        )
        assert run.scope_id == "grade4_maths"
        assert run.status == "planned"
        session.add.assert_called()
        session.flush.assert_called()

        # 2. Get run found
        session.get.return_value = run
        fetched = await service.get_run(session, run.run_id)
        assert fetched == run

        # 3. Get run not found -> LookupError
        session.get.return_value = None
        with pytest.raises(LookupError, match="not found"):
            await service.get_run(session, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_list_runs(self):
        service = ContentGenerationRunService()
        session = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalars.return_value.all.return_value = ["run1", "run2"]
        session.execute.return_value = mock_res

        # with and without scope_id
        runs1 = await service.list_runs(session, scope_id="grade4_maths")
        assert len(runs1) == 2
        runs2 = await service.list_runs(session, scope_id=None)
        assert len(runs2) == 2

    @pytest.mark.asyncio
    async def test_create_tasks_and_manage_states(self):
        mock_registry = MagicMock()
        mock_registry.get_scope_caps_refs.return_value = ["4.MATH.1.1"]
        service = ContentGenerationRunService(scope_registry=mock_registry)
        session = AsyncMock()

        run_id = uuid.uuid4()
        run = ContentGenerationRun(
            run_id=run_id,
            scope_id="grade4_maths",
            requested_by="admin",
            status="created",
            run_metadata={"layers": ["lessons"], "dry_run": False},
        )
        session.get.return_value = run

        # 1. First call: no existing tasks -> creates new tasks
        mock_empty_res = MagicMock()
        mock_empty_res.scalars.return_value.all.return_value = []
        session.execute.return_value = mock_empty_res

        tasks = await service.create_tasks_for_run(session, run_id)
        assert len(tasks) == 1
        assert tasks[0].content_layer == "lessons"
        assert tasks[0].status == "queued"

        # 2. Second call: existing tasks returned
        mock_existing_res = MagicMock()
        mock_existing_res.scalars.return_value.all.return_value = tasks
        session.execute.return_value = mock_existing_res
        tasks_again = await service.create_tasks_for_run(session, run_id)
        assert tasks_again == tasks

    @pytest.mark.asyncio
    async def test_task_status_transitions(self):
        service = ContentGenerationRunService()
        session = AsyncMock()
        task_id = uuid.uuid4()
        task = ContentGenerationTask(
            task_id=task_id,
            run_id=uuid.uuid4(),
            scope_id="s1",
            caps_ref="4.MATH.1.1",
            content_layer="lessons",
            status="queued",
            attempt_number=1,
            max_attempts=3,
        )
        session.get.return_value = task

        # mark queued
        await service.mark_task_queued(session, task_id)
        assert task.status == "queued"

        # mark running
        await service.mark_task_running(session, task_id)
        assert task.status == "running"
        assert task.started_at is not None

        # mark succeeded
        await service.mark_task_succeeded(session, task_id, ["art-1", "art-2"])
        assert task.status == "succeeded"
        assert task.output_artifact_ids == ["art-1", "art-2"]
        assert task.finished_at is not None

        # mark failed
        await service.mark_task_failed(session, task_id, "Syntax error in generation")
        assert task.status == "failed"
        assert task.validation_failures == ["Syntax error in generation"]

        # invalid status -> ValueError
        with pytest.raises(ValueError, match="Unsupported task status"):
            await service._mark_task(session, task_id, "invalid_state")

        # task not found -> LookupError
        session.get.return_value = None
        with pytest.raises(LookupError, match="not found"):
            await service._mark_task(session, task_id, "queued")

    @pytest.mark.asyncio
    async def test_cancel_and_retry_runs(self):
        service = ContentGenerationRunService()
        session = AsyncMock()
        run_id = uuid.uuid4()
        run = ContentGenerationRun(run_id=run_id, scope_id="s1", status="running", requested_by="admin")
        task_queued = ContentGenerationTask(
            task_id=uuid.uuid4(),
            run_id=run_id,
            scope_id="s1",
            caps_ref="4.M.1.1",
            content_layer="lessons",
            status="queued",
            attempt_number=1,
            max_attempts=3,
        )
        task_failed = ContentGenerationTask(
            task_id=uuid.uuid4(),
            run_id=run_id,
            scope_id="s1",
            caps_ref="4.M.1.2",
            content_layer="lessons",
            status="failed",
            attempt_number=1,
            max_attempts=3,
        )
        session.get.return_value = run

        # 1. Cancel run
        mock_tasks_res = MagicMock()
        mock_tasks_res.scalars.return_value.all.return_value = [task_queued]
        session.execute.return_value = mock_tasks_res

        cancelled_run = await service.cancel_run(session, run_id, "admin")
        assert cancelled_run.status == "cancelled"
        assert task_queued.status == "cancelled"

        # 2. Retry failed tasks
        mock_tasks_res2 = MagicMock()
        mock_tasks_res2.scalars.return_value.all.return_value = [task_failed]
        session.execute.return_value = mock_tasks_res2

        retries = await service.retry_failed_tasks(session, run_id, "admin")
        assert len(retries) == 1
        assert retries[0].attempt_number == 2
        assert retries[0].status == "queued"
