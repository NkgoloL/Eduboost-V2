import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user

pytestmark = pytest.mark.unit


class FakeRun:
    def __init__(self):
        self.run_id = uuid.uuid4(); self.scope_id = "grade4_mathematics_en"; self.status = "planned"; self.requested_by = "admin"; self.run_metadata = {"dry_run": True}


class FakeTask:
    def __init__(self, run_id):
        self.task_id = uuid.uuid4(); self.run_id = run_id; self.scope_id = "grade4_mathematics_en"; self.caps_ref = "4.M.1.1"; self.content_layer = "diagnostic_items"; self.status = "queued"; self.attempt_number = 1; self.max_attempts = 3; self.output_artifact_ids = []; self.validation_failures = []


class FakeRunService:
    def __init__(self):
        self.run = FakeRun(); self.tasks = [FakeTask(self.run.run_id)]
    async def list_runs(self, session, scope_id=None): return [self.run]
    async def create_run(self, session, **kwargs): return self.run
    async def create_tasks_for_run(self, session, run_id): return self.tasks
    async def get_run(self, session, run_id): return self.run
    async def get_run_tasks(self, session, run_id): return self.tasks
    async def cancel_run(self, session, run_id, actor_id): self.run.status = "cancelled"; return self.run
    async def retry_failed_tasks(self, session, run_id, actor_id): return self.tasks


class FakeSession:
    async def commit(self): return None


def _admin_user(): return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}
def _fake_session(): return FakeSession()
def _fake_run_service(): return FakeRunService()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear(); app.openapi_schema = None
    yield
    app.dependency_overrides.clear(); app.openapi_schema = None


def test_admin_can_list_runs() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_content_generation_run_service] = _fake_run_service
    response = TestClient(app, raise_server_exceptions=False).get("/api/v2/admin/content-factory/runs")
    assert response.status_code == 200
    assert response.json()["data"][0]["status"] == "planned"


def test_admin_can_create_dry_run_run() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_content_generation_run_service] = _fake_run_service
    response = TestClient(app, raise_server_exceptions=False).post("/api/v2/admin/content-factory/runs", json={"scope_id": "grade4_mathematics_en", "layers": ["diagnostic_items"], "dry_run": True})
    assert response.status_code == 200
    assert response.json()["data"]["scope_id"] == "grade4_mathematics_en"


def test_admin_can_inspect_run_tasks() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_content_generation_run_service] = _fake_run_service
    response = TestClient(app, raise_server_exceptions=False).get(f"/api/v2/admin/content-factory/runs/{uuid.uuid4()}/tasks")
    assert response.status_code == 200
    assert response.json()["data"][0]["status"] == "queued"
