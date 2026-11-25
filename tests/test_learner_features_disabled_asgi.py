from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core.config import Settings, settings
from app.core.feature_gates import require_learner_diagnostic_enabled


@pytest.fixture
def client():
    # Canonical production app; no minimal FastAPI app and no dependency overrides.
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("get", "/api/v2/diagnostics/items/00000000-0000-0000-0000-000000000001", {}),
        ("post", "/api/v2/diagnostics/sessions", {"json": {"learner_id": "00000000-0000-0000-0000-000000000001", "caps_ref": "4.M.1.1"}}),
        ("get", "/api/v2/learners/00000000-0000-0000-0000-000000000001/mastery", {}),
        ("get", "/api/v2/parents/learners/00000000-0000-0000-0000-000000000001/progress", {}),
        ("get", "/api/v2/vertical-journey/learners/00000000-0000-0000-0000-000000000001", {}),
        ("get", "/api/v2/assessments", {}),
        ("get", "/api/v2/onboarding/questions", {}),
        ("post", "/api/v2/practice/sessions", {"json": {"learner_id": "00000000-0000-0000-0000-000000000001", "gap_topics": [], "theta": 0.0}}),
        ("get", "/api/v2/learner/content/scopes/grade4_mathematics_en/diagnostic-items", {}),
    ],
)
def test_canonical_asgi_denies_disabled_diagnostic_and_mastery_paths(client, method, path, kwargs):
    response = getattr(client, method)(path, **kwargs)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "feature_disabled"


def test_disabled_features_are_default_off():
    assert settings.LEARNER_DIAGNOSTIC_ENABLED is False
    assert settings.LEARNER_MASTERY_VIEW_ENABLED is False
    assert settings.LEARNER_PILOT_AUTHORIZATION is False


def test_settings_reject_enabled_features_without_pilot_authorization():
    with pytest.raises(ValueError, match="LEARNER_PILOT_AUTHORIZATION"):
        Settings(LEARNER_DIAGNOSTIC_ENABLED=True)
    with pytest.raises(ValueError, match="LEARNER_PILOT_AUTHORIZATION"):
        Settings(LEARNER_MASTERY_VIEW_ENABLED=True)


def test_gate_mutation_is_observable_in_process(client):
    calls = []

    def permissive_mutation():
        calls.append("diagnostic gate bypass installed")

    app.dependency_overrides[require_learner_diagnostic_enabled] = permissive_mutation
    try:
        response = client.get("/api/v2/diagnostics/items/00000000-0000-0000-0000-000000000001")
        assert calls == ["diagnostic gate bypass installed"]
        # Without the feature gate, execution proceeds to authentication instead.
        assert response.status_code == 401
        assert response.json()["error"]["code"] != "feature_disabled"
    finally:
        app.dependency_overrides.pop(require_learner_diagnostic_enabled, None)


@pytest.mark.asyncio
async def test_study_plan_does_not_read_mastery():
    from types import SimpleNamespace
    from app.services.study_plan_service_v2 import StudyPlanServiceV2

    class LearnerRepo:
        async def get_by_id(self, learner_id):
            return SimpleNamespace(grade=4)

    class PlanRepo:
        def __init__(self):
            self.mastery_called = False

        async def get_subject_mastery(self, learner_id):
            self.mastery_called = True
            raise AssertionError("disabled mastery must not be read")

        async def create(self, **kwargs):
            return {"plan_id": "test", **kwargs}

    plans = PlanRepo()
    plan = await StudyPlanServiceV2(LearnerRepo(), plans).generate_plan("learner")
    assert plans.mastery_called is False
    assert plan["gap_ratio"] == 0.0
    assert "Focus on" not in plan["week_focus"]
