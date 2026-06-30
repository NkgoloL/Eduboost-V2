
import pytest

from app.domain.content_coverage import ContentLayer
from app.services.content_generation_runs import ContentGenerationRunService


class FakeRegistry:
    def validate_scope_exists(self, scope_id: str) -> None:
        if scope_id != "grade4_mathematics_en":
            raise LookupError(scope_id)

    def get_scope_caps_refs(self, scope_id: str) -> list[str]:
        return ["4.M.1.1", "4.M.1.2"]


class FakeSession:
    def __init__(self) -> None:
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

    async def flush(self):
        return None

    async def get(self, model, item_id):
        return next((obj for obj in self.objects if getattr(obj, "run_id", None) == item_id or getattr(obj, "task_id", None) == item_id), None)

    async def execute(self, stmt):
        class Result:
            def __init__(self, rows):
                self.rows = rows
            def scalars(self):
                return self
            def all(self):
                return self.rows
        return Result([obj for obj in self.objects if obj.__class__.__name__ == "ContentGenerationTask"])


@pytest.mark.asyncio
async def test_create_run_and_tasks_are_idempotent() -> None:
    session = FakeSession()
    service = ContentGenerationRunService(FakeRegistry())
    run = await service.create_run(session, scope_id="grade4_mathematics_en", layers=[ContentLayer.DIAGNOSTIC_ITEMS], requested_by="admin")
    tasks = await service.create_tasks_for_run(session, run.run_id)
    again = await service.create_tasks_for_run(session, run.run_id)
    assert len(tasks) == 2
    assert again == tasks


@pytest.mark.asyncio
async def test_cancel_run_cancels_queued_tasks() -> None:
    session = FakeSession()
    service = ContentGenerationRunService(FakeRegistry())
    run = await service.create_run(session, scope_id="grade4_mathematics_en", layers=[ContentLayer.DIAGNOSTIC_ITEMS], requested_by="admin")
    await service.create_tasks_for_run(session, run.run_id)
    cancelled = await service.cancel_run(session, run.run_id, "admin")
    assert cancelled.status == "cancelled"
    assert all(task.status == "cancelled" for task in session.objects if hasattr(task, "task_id"))
