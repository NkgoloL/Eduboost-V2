from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for diagnostic items read authorization."""

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import diagnostics as diagnostics_router


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
            grade=4,
        )


class FakeIRTRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_items_for_grade(self, grade: int, limit: int | None = None) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                id="item-1",
                question_text="What is 1 + 1?",
                options=["1", "2", "3", "4"],
                subject="MATH",
                topic="Addition",
                skill="Addition",
                b_param=0.0,
                a_param=1.0,
                caps_reference="CAPS-MATH-4",
                grade=grade,
                review_status="approved",
            )
        ]


class FakeCAPSValidator:
    def validate(self, grade: int, subject: str, topic: str) -> SimpleNamespace:
        return SimpleNamespace(caps_reference="CAPS-MATH-4")


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def diagnostic_items_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(diagnostics_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    monkeypatch.setattr(diagnostics_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(diagnostics_router, "IRTRepository", FakeIRTRepository)
    monkeypatch.setattr(diagnostics_router, "_caps_validator", FakeCAPSValidator())
    app.dependency_overrides[diagnostics_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_get_diagnostic_items_allows_admin_read() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )
    response = TestClient(app).get("/api/v2/diagnostics/items/learner-1")
    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload[0]["id"] == "item-1"


@pytest.mark.integration
def test_get_diagnostic_items_allows_assigned_guardian_read() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )
    response = TestClient(app).get("/api/v2/diagnostics/items/learner-1")
    assert response.status_code == 200


@pytest.mark.integration
def test_get_diagnostic_items_allows_learner_self_read() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )
    response = TestClient(app).get("/api/v2/diagnostics/items/learner-1")
    assert response.status_code == 200


@pytest.mark.integration
def test_get_diagnostic_items_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )
    response = TestClient(app).get("/api/v2/diagnostics/items/learner-1")
    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_get_diagnostic_items_rejects_missing_auth() -> None:
    response = TestClient(app).get("/api/v2/diagnostics/items/learner-1")
    assert response.status_code == 401


@pytest.mark.integration
def test_get_diagnostic_items_preserves_not_found() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )
    response = TestClient(app).get("/api/v2/diagnostics/items/missing-learner")
    assert response.status_code == 404
