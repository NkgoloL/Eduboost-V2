import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user

pytestmark = pytest.mark.unit


class FakeGate:
    passed = False
    errors = ["coverage red"]
    summary = {"scope_id": "grade4_mathematics_en"}


class FakeSeedRun:
    seed_run_id = uuid.uuid4(); scope_id = "grade4_mathematics_en"; dry_run = True; status = "blocked"; summary = {"errors": ["coverage red"]}


class FakeSeedService:
    async def dry_run_seed(self, session, scope_id, layer=None): return FakeSeedRun()
    async def seed_staging(self, session, scope_id, actor_id): raise ValueError("gate failed")
    async def verify_staging_seed(self, session, scope_id): return FakeGate()
    async def promote_production(self, session, scope_id, actor_id): raise ValueError("staging not verified")


class FakeSession:
    async def commit(self): return None


def _admin_user(): return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}
def _fake_session(): return FakeSession()
def _fake_seed_service(): return FakeSeedService()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear(); app.openapi_schema = None
    yield
    app.dependency_overrides.clear(); app.openapi_schema = None


def test_seed_staging_fails_if_gate_unmet() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_seed_promotion_service] = _fake_seed_service
    response = TestClient(app, raise_server_exceptions=False).post("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/seed-staging")
    assert response.status_code == 409


def test_promote_production_fails_if_staging_not_verified() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_seed_promotion_service] = _fake_seed_service
    response = TestClient(app, raise_server_exceptions=False).post("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/promote-production")
    assert response.status_code == 409
