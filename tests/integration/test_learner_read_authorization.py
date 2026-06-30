from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for learner read object authorization."""

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import learners as learners_router


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> None:
        return None


class FakeLearnerRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_by_id(self, learner_id: str) -> SimpleNamespace | None:
        if learner_id == "missing-learner":
            return None

        return SimpleNamespace(
            id=learner_id,
            guardian_id="guardian-1",
            pseudonym_id=f"pseudo-{learner_id}",
            display_name="Pilot Learner",
            grade=4,
            language="en",
            archetype=None,
            theta=0.0,
            xp=0,
            streak_days=0,
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def learner_route_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(learners_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    monkeypatch.setattr(learners_router, "LearnerRepository", FakeLearnerRepository)

    app.dependency_overrides[learners_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_get_learner_allows_admin_read() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/learners/learner-1")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["id"] == "learner-1"


@pytest.mark.integration
def test_get_learner_allows_assigned_guardian_read() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/learners/learner-1")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["id"] == "learner-1"


@pytest.mark.integration
def test_get_learner_allows_self_learner_read() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )

    response = TestClient(app).get("/api/v2/learners/learner-1")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["id"] == "learner-1"


@pytest.mark.integration
def test_get_learner_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/learners/learner-1")

    assert response.status_code == 403
    body = response.json()
    assert "object_forbidden" in str(body)


@pytest.mark.integration
def test_get_learner_rejects_missing_auth() -> None:
    response = TestClient(app).get("/api/v2/learners/learner-1")

    assert response.status_code == 401


@pytest.mark.integration
def test_get_learner_preserves_not_found_for_missing_learner() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/learners/missing-learner")

    assert response.status_code == 404
    assert "Learner not found" in str(response.json())
