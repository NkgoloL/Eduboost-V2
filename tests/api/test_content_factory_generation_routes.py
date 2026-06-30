from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user
from app.services.content_generation_executor import GenerationDisabledError, RunExecutionResult, TaskExecutionResult
from app.services.content_generation_planner import GenerationPlanResult

pytestmark = pytest.mark.unit


class FakeSession:
    async def commit(self):
        return None
    async def get(self, model, key):
        return None


class FakePlanner:
    async def plan_missing_for_run(self, session, run_id, *, actor_id=None):
        return GenerationPlanResult(run_id=run_id, created_task_ids=[uuid.uuid4()], skipped=[], missing=[{"scope_id": "grade4_mathematics_en"}])


class DisabledExecutor:
    async def execute_run(self, *args, **kwargs):
        raise GenerationDisabledError("Set CONTENT_FACTORY_GENERATION_ENABLED=true to execute generation tasks.")
    async def execute_task(self, *args, **kwargs):
        raise GenerationDisabledError("Set CONTENT_FACTORY_GENERATION_ENABLED=true to execute generation tasks.")
    async def execution_report(self, session, run_id):
        return {"run_id": str(run_id), "status": "planned", "tasks": 1, "queued": 1, "succeeded": 0, "failed": 0, "skipped": 0, "artifacts": 0}


class EnabledExecutor:
    async def execute_run(self, session, run_id, max_tasks=None, actor_id=None):
        return RunExecutionResult(run_id, "succeeded", [], {"tasks_executed": 1, "artifacts_created": 1})
    async def execute_task(self, session, task_id, actor_id=None):
        return TaskExecutionResult(task_id, "succeeded", [uuid.uuid4()], [], "deterministic", "deterministic")
    async def execution_report(self, session, run_id):
        return {"run_id": str(run_id), "status": "succeeded", "tasks": 1, "queued": 0, "succeeded": 1, "failed": 0, "skipped": 0, "artifacts": 1}


def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


def _parent_user():
    return {"sub": str(uuid.uuid4()), "role": "parent", "type": "access"}


def _session():
    return FakeSession()


def _planner():
    return FakePlanner()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def _client():
    return TestClient(app, raise_server_exceptions=False)


def test_unauthenticated_generation_route_rejected() -> None:
    response = _client().post(f"/api/v2/admin/content-factory/runs/{uuid.uuid4()}/plan-missing")
    assert response.status_code == 401


def test_non_admin_generation_route_rejected() -> None:
    app.dependency_overrides[get_current_user] = _parent_user
    response = _client().post(f"/api/v2/admin/content-factory/runs/{uuid.uuid4()}/plan-missing")
    assert response.status_code == 403


def test_admin_can_plan_missing_tasks() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _session
    app.dependency_overrides[content_factory.get_content_generation_planner] = _planner
    response = _client().post(f"/api/v2/admin/content-factory/runs/{uuid.uuid4()}/plan-missing")

    assert response.status_code == 200
    assert response.json()["data"]["created_task_ids"]


def test_execute_returns_disabled_response_when_flag_false() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _session
    app.dependency_overrides[content_factory.get_content_generation_executor] = lambda: DisabledExecutor()
    response = _client().post(f"/api/v2/admin/content-factory/runs/{uuid.uuid4()}/execute")

    assert response.status_code == 409
    assert response.json()["error"]["details"]["error"] == "generation_disabled"


def test_deterministic_execution_works_when_enabled() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _session
    app.dependency_overrides[content_factory.get_content_generation_executor] = lambda: EnabledExecutor()
    response = _client().post(f"/api/v2/admin/content-factory/tasks/{uuid.uuid4()}/execute")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "succeeded"
    assert response.json()["data"]["artifact_ids"]


def test_execution_report_returns_task_and_artifact_counts() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _session
    app.dependency_overrides[content_factory.get_content_generation_executor] = lambda: EnabledExecutor()
    response = _client().get(f"/api/v2/admin/content-factory/runs/{uuid.uuid4()}/execution-report")

    assert response.status_code == 200
    assert response.json()["data"]["tasks"] == 1
    assert response.json()["data"]["artifacts"] == 1
