from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user


class FakeSession:
    async def commit(self):
        return None

class FakeVerificationService:
    async def verify_seed_run(self, session, seed_run_id, actor_id=None):
        return SimpleNamespace(seed_run_id=seed_run_id, passed=True, verified_count=1, errors=[])
    async def verify_scope_staging(self, session, scope_id):
        return SimpleNamespace(scope_id=scope_id, passed=True, staged_artifacts_count=1, errors=[])

class FakeSeedExecutor:
    async def dry_run_seed(self, session, scope_id, actor_id=None):
        return SimpleNamespace(scope_id=scope_id, layers=["test"], seedable=[], skipped=[])
    async def seed_staging(self, session, scope_id, actor_id=None, allow_partial=True):
        return SimpleNamespace(seed_run_id=uuid.uuid4(), scope_id=scope_id, status="seeded", seeded_count=1, skipped_count=0, errors=[])
    async def list_seed_runs(self, session, scope_id=None, limit=50, offset=0):
        return SimpleNamespace(items=[], total=0, limit=50, offset=0)
    async def get_seed_run(self, session, seed_run_id):
        return SimpleNamespace(seed_run_id=seed_run_id, scope_id="scope", status="seeded", seeded_count=1, skipped_count=0)
    async def list_seed_run_items(self, session, seed_run_id):
        return [SimpleNamespace(id=uuid.uuid4(), seed_run_id=seed_run_id, artifact_id=uuid.uuid4(), scope_id="scope", caps_ref="4.M.1.1", layer="diagnostic_items", artifact_type="diagnostic_item", target_table="content_staging_artifacts", target_record_id=str(uuid.uuid4()), status="seeded", skip_reason=None, seed_payload_hash="hash")]
    async def rollback_seed_run(self, session, seed_run_id, actor_id, reason):
        return SimpleNamespace(seed_run_id=seed_run_id, status="rolled_back", rolled_back_count=1)

def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}

def _parent_user():
    return {"sub": str(uuid.uuid4()), "role": "parent", "type": "access"}

def _session():
    return FakeSession()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def _client():
    return TestClient(app, raise_server_exceptions=False)


def _wire_admin():
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _session
    app.dependency_overrides[content_factory.get_content_staging_seed_executor] = lambda: FakeSeedExecutor()
    app.dependency_overrides[content_factory.get_content_staging_read_verification_service] = lambda: FakeVerificationService()

def test_unauthenticated_dry_run_rejected():
    assert _client().post("/api/v2/admin/content-factory/scopes/grade4/dry-run-seed").status_code == 401

def test_non_admin_dry_run_rejected():
    app.dependency_overrides[get_current_user] = _parent_user
    assert _client().post("/api/v2/admin/content-factory/scopes/grade4/dry-run-seed").status_code == 403

def test_admin_can_dry_run_seed():
    _wire_admin()
    response = _client().post("/api/v2/admin/content-factory/scopes/grade4/dry-run-seed")
    assert response.status_code == 200
    assert response.json()["data"]["scope_id"] == "grade4"

def test_admin_can_seed_staging():
    _wire_admin()
    response = _client().post("/api/v2/admin/content-factory/scopes/grade4/seed-staging")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "seeded"
    assert response.json()["data"]["seeded_count"] == 1

def test_admin_can_verify_seed_run():
    _wire_admin()
    run_id = str(uuid.uuid4())
    response = _client().post(f"/api/v2/admin/content-factory/seed-runs/{run_id}/verify")
    assert response.status_code == 200
    assert response.json()["data"]["passed"] is True

def test_admin_can_fetch_seed_run_items():
    _wire_admin()
    run_id = str(uuid.uuid4())
    response = _client().get(f"/api/v2/admin/content-factory/seed-runs/{run_id}/items")
    assert response.status_code == 200
    assert response.json()["data"][0]["status"] == "seeded"

def test_admin_can_rollback_seed_run():
    _wire_admin()
    run_id = str(uuid.uuid4())
    response = _client().post(f"/api/v2/admin/content-factory/seed-runs/{run_id}/rollback?reason=test")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "rolled_back"
