from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for learner mastery object authorization."""

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


class FakeKnowledgeGapRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_active_gaps(self, learner_id: str) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(subject="MATH", severity=0.5),
            SimpleNamespace(subject="ENG", severity=0.25),
        ]


class FakeMasteryRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_mastery_for_learner(self, learner_id: str) -> dict:
        return {"mastery": 0.75, "subject_mastery": {"MATH": 0.8, "ENG": 0.7}}

    async def list_topic_mastery_by_learner(self, learner_id: str) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                topic="fractions",
                mastery_score=0.9,
                caps_ref="M4.1.1",
                mastery_label="Highly Proficient",
                last_updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ),
            SimpleNamespace(
                topic="geometry",
                mastery_score=0.6,
                caps_ref="M4.3.2",
                mastery_label="Developing",
                last_updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ),
        ]


class FakeDB:
    async def commit(self) -> None:
        return None

    def expire_all(self) -> None:
        return None


async def override_db() -> object:
    return FakeDB()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def learner_mastery_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(learners_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    monkeypatch.setattr(learners_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(
        learners_router,
        "KnowledgeGapRepository",
        FakeKnowledgeGapRepository,
    )
    monkeypatch.setattr(learners_router, "MasteryRepository", FakeMasteryRepository)

    app.dependency_overrides[learners_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_get_mastery_allows_admin_read() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/learners/learner-1/mastery")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["learner_id"] == "learner-1"
    assert payload["mastery"]


@pytest.mark.integration
def test_get_mastery_allows_assigned_guardian_read() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/learners/learner-1/mastery")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["learner_id"] == "learner-1"


@pytest.mark.integration
def test_get_mastery_allows_self_learner_read() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )

    response = TestClient(app).get("/api/v2/learners/learner-1/mastery")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["learner_id"] == "learner-1"


@pytest.mark.integration
def test_get_mastery_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/learners/learner-1/mastery")

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_get_mastery_rejects_missing_auth() -> None:
    response = TestClient(app).get("/api/v2/learners/learner-1/mastery")

    assert response.status_code == 401


@pytest.mark.integration
def test_get_mastery_preserves_not_found_for_missing_learner() -> None:
    app.dependency_overrides[learners_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/learners/missing-learner/mastery")

    assert response.status_code == 404
    assert "Learner not found" in str(response.json())
