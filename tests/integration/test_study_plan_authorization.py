"""HTTP contract tests for study-plan write authorization."""
from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import study_plans as study_plans_router


async def fake_enqueue_job(background_tasks, *, operation: str, payload: dict, handler):
    return {
        "job_id": "job-study-plan-1",
        "operation": operation,
        "status": "queued",
        "payload": payload,
    }


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def study_plan_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(study_plans_router, "enqueue_job", fake_enqueue_job)
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_generate_study_plan_allows_admin_write() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).post(
        "/api/v2/study-plans/learner-1",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 202
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["job_id"] == "job-study-plan-1"


@pytest.mark.integration
def test_generate_study_plan_allows_guardian_with_learner_claim() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {
            "sub": "guardian-1",
            "role": "parent",
            "guardian_learner_ids": ["learner-1"],
        }
    )

    response = TestClient(app).post(
        "/api/v2/study-plans/learner-1",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_study_plan_allows_legacy_generate_alias() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {
            "sub": "guardian-1",
            "role": "parent",
            "guardian_learner_ids": ["learner-1"],
        }
    )

    response = TestClient(app).post(
        "/api/v2/study-plans/generate/learner-1",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_study_plan_allows_learner_self_write() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )

    response = TestClient(app).post(
        "/api/v2/study-plans/learner-1",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_study_plan_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {
            "sub": "guardian-1",
            "role": "parent",
            "guardian_learner_ids": ["learner-2"],
        }
    )

    response = TestClient(app).post(
        "/api/v2/study-plans/learner-1",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_generate_study_plan_rejects_missing_auth() -> None:
    response = TestClient(app).post(
        "/api/v2/study-plans/learner-1",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 401
