from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for study-plan write authorization."""

from typing import Any

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import study_plans as study_plans_router


LEARNER_1 = "00000000-0000-0000-0000-000000000001"
LEARNER_2 = "00000000-0000-0000-0000-000000000002"
GUARDIAN_1 = "00000000-0000-0000-0000-000000000003"
ADMIN_1 = "00000000-0000-0000-0000-000000000004"


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
    monkeypatch.setattr(study_plans_router, "require_active_consent_for_current_user", AsyncMock())
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_generate_study_plan_allows_admin_write() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {"sub": ADMIN_1, "role": "admin"}
    )

    response = TestClient(app).post(
        f"/api/v2/study-plans/{LEARNER_1}",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["data"]["job_id"] == "job-study-plan-1"


@pytest.mark.integration
def test_generate_study_plan_allows_guardian_with_learner_claim() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {
            "sub": GUARDIAN_1,
            "role": "parent",
            "guardian_learner_ids": [LEARNER_1],
        }
    )

    response = TestClient(app).post(
        f"/api/v2/study-plans/{LEARNER_1}",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_study_plan_allows_legacy_generate_alias() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {
            "sub": GUARDIAN_1,
            "role": "parent",
            "guardian_learner_ids": [LEARNER_1],
        }
    )

    response = TestClient(app).post(
        f"/api/v2/study-plans/generate/{LEARNER_1}",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_study_plan_allows_learner_self_write() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {"sub": LEARNER_1, "role": "student"}
    )

    response = TestClient(app).post(
        f"/api/v2/study-plans/{LEARNER_1}",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_study_plan_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[study_plans_router.get_current_user] = override_user(
        {
            "sub": GUARDIAN_1,
            "role": "parent",
            "guardian_learner_ids": [LEARNER_2],
        }
    )

    response = TestClient(app).post(
        f"/api/v2/study-plans/{LEARNER_1}",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_generate_study_plan_rejects_missing_auth() -> None:
    response = TestClient(app).post(
        f"/api/v2/study-plans/{LEARNER_1}",
        json={"gap_ratio": 0.4},
    )

    assert response.status_code == 401
