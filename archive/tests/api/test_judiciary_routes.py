from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
import app.core.dependencies as core_deps
from app.models import UserRole

# Provide a compatibility alias for RequireRole so importing the router works in tests
def _require_role_stub(_roles):
    def _inner(*args, **kwargs):
        return None
    return _inner

core_deps.RequireRole = _require_role_stub

# Provide a fake `app.services.judiciary_service_v2` module so the router can import
import sys
import types

fake_mod = types.ModuleType("app.services.judiciary_service_v2")
class _FakeSvc:
    async def screen_content(self, text):
        return True

fake_mod.JudiciaryServiceV2 = lambda: _FakeSvc()
sys.modules["app.services.judiciary_service_v2"] = fake_mod

from app.api_v2_routers import judiciary as judiciary_module
# Register judiciary router on test app so endpoints resolve (use router's prefix)
app.include_router(judiciary_module.router)


pytestmark = pytest.mark.unit


def _client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


class DummyAuth:
    def __init__(self, roles):
        self.roles = roles


def test_screen_content_forbidden_for_non_admin(monkeypatch):
    async def fake_auth():
        return DummyAuth([UserRole.STUDENT])

    app.dependency_overrides[judiciary_module.require_auth_context] = fake_auth

    resp = _client().post("/api/v2/judiciary/screen", params={"text": "bad"})
    assert resp.status_code == 403


def test_screen_content_calls_service(monkeypatch):
    class FakeSvc:
        async def screen_content(self, text):
            return True

    monkeypatch.setattr(judiciary_module, "JudiciaryServiceV2", lambda: FakeSvc())

    async def fake_auth():
        return DummyAuth([UserRole.ADMIN])

    app.dependency_overrides[judiciary_module.require_auth_context] = fake_auth

    resp = _client().post("/api/v2/judiciary/screen", params={"text": "ok"})
    assert resp.status_code == 200
    assert resp.json()["data"]["is_safe"] is True
