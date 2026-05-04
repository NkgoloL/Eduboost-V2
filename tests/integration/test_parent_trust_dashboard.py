from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core.database import get_db
from app.core.security import require_parent_or_admin


class _ScalarListResult:
    def __init__(self, values):
        self._values = values

    def scalars(self):
        return self

    def all(self):
        return self._values


def test_parent_trust_dashboard_returns_gap_summary_and_export_links(monkeypatch):
    guardian = SimpleNamespace(id="guardian-1", subscription_tier="premium")
    learner = SimpleNamespace(
        id="learner-1",
        display_name="Anele",
        grade=4,
        archetype="Keter",
        theta=0.42,
        pseudonym_id="pseudo-1",
        streak_days=6,
    )

    class FakeDB:
        def __init__(self):
            self.scalar_calls = 0

        async def get(self, _model, record_id):
            if record_id == "guardian-1":
                return guardian
            return None

        async def execute(self, _stmt):
            return _ScalarListResult(
                [SimpleNamespace(topic="fractions"), SimpleNamespace(topic="geometry")]
            )

        async def scalar(self, _stmt):
            self.scalar_calls += 1
            return 4 if self.scalar_calls == 1 else 3

    async def override_db():
        yield FakeDB()

    def override_user():
        return {"sub": "guardian-1", "role": "parent"}

    class FakeLearnerRepository:
        def __init__(self, _db):
            pass

        async def get_by_guardian(self, _guardian_id):
            return [learner]

    class FakeConsentService:
        def __init__(self, _db):
            pass

        async def require_active_consent(self, _learner_id, actor_id=None):
            return None

    monkeypatch.setattr("app.api_v2_routers.parents.LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr("app.api_v2_routers.parents.ConsentService", FakeConsentService)
    monkeypatch.setattr(
        "app.api_v2_routers.parents._executive.generate_progress_summary",
        AsyncMock(return_value="Steady progress with strong lesson follow-through."),
    )

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[require_parent_or_admin] = override_user

    with TestClient(app) as client:
        response = client.get("/api/v2/parents/guardian-1/dashboard")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["guardian_id"] == "guardian-1"
    assert payload["learners"][0]["top_knowledge_gaps"] == ["fractions", "geometry"]
    assert payload["learners"][0]["lesson_completion_rate_7d"] == 75.0
    assert payload["learners"][0]["export_url"].endswith("/api/v2/popia/data-export/learner-1")

