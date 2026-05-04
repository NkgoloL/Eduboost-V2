from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers.diagnostics import get_current_user


def test_diagnostic_submit_consumes_ai_quota(monkeypatch):
    learner = SimpleNamespace(id="learner-1", guardian_id="guardian-1", grade=4, theta=0.1, pseudonym_id="pseudo-1")
    item = SimpleNamespace(
        id="item-1",
        correct_option="A",
        subject="Mathematics",
        topic="fractions",
        a_param=1.1,
        b_param=0.0,
    )

    class FakeConsentService:
        def __init__(self, _db):
            pass

        async def require_active_consent(self, _learner_id):
            return None

    class FakeLearnerRepository:
        def __init__(self, _db):
            pass

        async def get_by_id(self, _learner_id):
            return learner

        async def update_theta(self, _learner_id, _theta):
            return None

    class FakeGuardianRepository:
        def __init__(self, _db):
            pass

        async def get_by_id(self, _guardian_id):
            return SimpleNamespace(subscription_tier="free")

    class FakeIRTRepository:
        def __init__(self, _db):
            pass

        async def get_items_for_grade(self, _grade, limit=20):
            return [item]

    class FakeDiagnosticRepository:
        def __init__(self, _db):
            pass

        async def create_session(self, _learner_id, theta_before):
            return SimpleNamespace(id="session-1", theta_before=theta_before)

        async def complete_session(self, _session_id, _responses, _theta_after):
            return None

    class FakeGapRepository:
        def __init__(self, _db):
            pass

        async def upsert(self, *_args, **_kwargs):
            return None

    quota_mock = AsyncMock()
    monkeypatch.setattr("app.api_v2_routers.diagnostics.ConsentService", FakeConsentService)
    monkeypatch.setattr("app.api_v2_routers.diagnostics.LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr("app.api_v2_routers.diagnostics.GuardianRepository", FakeGuardianRepository)
    monkeypatch.setattr("app.api_v2_routers.diagnostics.IRTRepository", FakeIRTRepository)
    monkeypatch.setattr("app.api_v2_routers.diagnostics.DiagnosticRepository", FakeDiagnosticRepository)
    monkeypatch.setattr("app.api_v2_routers.diagnostics.KnowledgeGapRepository", FakeGapRepository)
    monkeypatch.setattr("app.api_v2_routers.diagnostics.check_ai_quota", quota_mock)

    def override_user():
        return {"sub": "guardian-1"}

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as client:
        response = client.post(
            "/api/v2/diagnostics/submit",
            json={"learner_id": "learner-1", "answers": [{"item_id": "item-1", "selected_option": "A"}]},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    quota_mock.assert_awaited_once_with("guardian-1", "free")
