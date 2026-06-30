from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import ether as ether_module
from app.models import UserRole

# Register the router on the test app (use router's own prefix)
app.include_router(ether_module.router)


pytestmark = pytest.mark.unit


def _client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


class DummyAuth:
    def __init__(self, roles):
        self.roles = roles


def test_get_questions_calls_service(monkeypatch):
    # fake service
    class FakeService:
        async def get_onboarding_questions(self):
            return [{"id": 1, "text": "q"}]

    monkeypatch.setattr(ether_module, "EtherService", lambda: FakeService())

    async def fake_auth():
        return DummyAuth([UserRole.STUDENT])

    app.dependency_overrides[ether_module.require_auth_context] = fake_auth

    resp = _client().get("/api/v2/ether/onboarding/questions")
    assert resp.status_code == 200
    assert resp.json()["data"] == [{"id": 1, "text": "q"}]


def test_submit_onboarding_forbidden_for_role(monkeypatch):
    async def fake_auth():
        return DummyAuth([])

    app.dependency_overrides[ether_module.require_auth_context] = fake_auth

    resp = _client().post("/api/v2/ether/onboarding/submit", json={"archetype": "x", "description": "d"})
    assert resp.status_code == 403


def test_submit_onboarding_calls_service(monkeypatch):
    class FakeService:
        async def determine_archetype(self, response):
            return {"result": "ok"}

    monkeypatch.setattr(ether_module, "EtherService", lambda: FakeService())

    async def fake_auth():
        return DummyAuth([UserRole.STUDENT])

    app.dependency_overrides[ether_module.require_auth_context] = fake_auth

    resp = _client().post("/api/v2/ether/onboarding/submit", json={"archetype": "x", "description": "d"})
    assert resp.status_code == 200
    assert resp.json()["data"] == {"result": "ok"}
