from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for parent learner-progress authorization."""

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import parents as parents_router
from app.core.security import require_parent_or_admin


class FakeScalarResult:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows

    def all(self) -> list[tuple]:
        return self._rows


class FakeExecuteResult:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows

    def all(self) -> list[tuple]:
        return self._rows

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self._rows)


class FakeDB:
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, statement) -> FakeExecuteResult:
        self.calls += 1
        if self.calls == 1:
            return FakeExecuteResult([(datetime(2026, 1, 1, tzinfo=UTC), "MATH")])
        return FakeExecuteResult([("MATH", False), ("ENG", True)])
    async def commit(self) -> None:
        return None

    def expire_all(self) -> None:
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
            archetype=None,
            theta=0.4,
        )


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> None:
        return None


async def override_db() -> FakeDB:
    return FakeDB()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def parent_progress_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(parents_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(parents_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    app.dependency_overrides[parents_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_parent_progress_allows_admin_read() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/parents/learners/learner-1/progress")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["learner_id"] == "learner-1"


@pytest.mark.integration
def test_parent_progress_allows_assigned_guardian_read() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/parents/learners/learner-1/progress")

    assert response.status_code == 200


@pytest.mark.integration
def test_parent_progress_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/parents/learners/learner-1/progress")

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json()["error"])


@pytest.mark.integration
def test_parent_progress_rejects_missing_auth() -> None:
    response = TestClient(app).get("/api/v2/parents/learners/learner-1/progress")

    assert response.status_code == 401


@pytest.mark.integration
def test_parent_progress_preserves_not_found() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/parents/learners/missing-learner/progress")

    assert response.status_code == 404
