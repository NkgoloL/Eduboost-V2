"""HTTP contract tests for diagnostic submit write authorization."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import diagnostics as diagnostics_router

pytestmark = pytest.mark.integration


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
            theta=0.2,
        )

    async def update_theta(self, learner_id: str, theta: float) -> None:
        return None


class FakeGuardianRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_by_id(self, guardian_id: str) -> SimpleNamespace:
        return SimpleNamespace(id=guardian_id, subscription_tier="free")


class FakeIRTRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_items_for_grade(self, grade: int, limit: int | None = None) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                id="item-1",
                correct_option="A",
                subject="MATH",
                topic="Addition",
                grade=grade,
            )
        ]


class FakeDiagnosticRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def create_session(self, learner_id: str, theta: float) -> SimpleNamespace:
        return SimpleNamespace(id="session-1")

    async def complete_session(self, session_id: str, responses: dict[str, str], theta_after: float) -> None:
        return None


class FakeKnowledgeGapRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def upsert(self, learner_id: str, grade: int, subject: str, topic: str, severity: float) -> None:
        return None


class FakeEngine:
    def run_gap_probe_cascade(self, *, learner_grade: int, items: list, correct_item_ids: set, starting_theta: float) -> dict:
        return {
            "theta": 0.35,
            "standard_error": 0.2,
            "grade_equivalent": learner_grade,
            "ranked_gaps": [
                {"grade": learner_grade, "subject": "MATH", "topic": "Addition", "severity": 0.3}
            ],
        }


async def fake_check_ai_quota(guardian_id: str, tier: str) -> None:
    return None


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def diagnostic_submit_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(diagnostics_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    monkeypatch.setattr(
        diagnostics_router.diagnostic_repositories,
        "learner",
        lambda db: FakeLearnerRepository(db),
    )
    monkeypatch.setattr(
        diagnostics_router.diagnostic_repositories,
        "guardian",
        lambda db: FakeGuardianRepository(db),
    )
    monkeypatch.setattr(
        diagnostics_router.diagnostic_repositories,
        "irt",
        lambda db: FakeIRTRepository(db),
    )
    monkeypatch.setattr(
        diagnostics_router.diagnostic_repositories,
        "diagnostic",
        lambda db: FakeDiagnosticRepository(db),
    )
    monkeypatch.setattr(
        diagnostics_router.diagnostic_repositories,
        "knowledge_gap",
        lambda db: FakeKnowledgeGapRepository(db),
    )
    monkeypatch.setattr(diagnostics_router, "_engine", FakeEngine())
    monkeypatch.setattr(diagnostics_router, "check_ai_quota", fake_check_ai_quota)
    app.dependency_overrides[diagnostics_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


def diagnostic_payload(learner_id: str = "learner-1") -> dict[str, Any]:
    return {
        "learner_id": learner_id,
        "answers": [{"item_id": "item-1", "selected_option": "A"}],
    }


@pytest.mark.integration
def test_submit_diagnostic_allows_admin_write() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).post("/api/v2/diagnostics/submit", json=diagnostic_payload())

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["session_id"] == "session-1"


@pytest.mark.integration
def test_submit_diagnostic_allows_guardian_with_claim() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent", "guardian_learner_ids": ["learner-1"]}
    )

    response = TestClient(app).post("/api/v2/diagnostics/submit", json=diagnostic_payload())

    assert response.status_code == 200


@pytest.mark.integration
def test_submit_diagnostic_allows_learner_self_write() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )

    response = TestClient(app).post("/api/v2/diagnostics/submit", json=diagnostic_payload())

    assert response.status_code == 200


@pytest.mark.integration
def test_submit_diagnostic_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent", "guardian_learner_ids": ["learner-2"]}
    )

    response = TestClient(app).post("/api/v2/diagnostics/submit", json=diagnostic_payload())

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_submit_diagnostic_rejects_missing_auth() -> None:
    response = TestClient(app).post("/api/v2/diagnostics/submit", json=diagnostic_payload())

    assert response.status_code == 401


@pytest.mark.integration
def test_submit_diagnostic_preserves_not_found() -> None:
    app.dependency_overrides[diagnostics_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).post(
        "/api/v2/diagnostics/submit",
        json=diagnostic_payload("missing-learner"),
    )

    assert response.status_code == 404
