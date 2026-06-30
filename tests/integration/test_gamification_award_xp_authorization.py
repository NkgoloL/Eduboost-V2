from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for gamification award-xp write authorization."""

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import gamification as gamification_router


class FakeDB:
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
        return SimpleNamespace(id=learner_id, guardian_id="guardian-1", pseudonym_id=f"pseudo-{learner_id}")

    async def add_xp(self, learner_id: str, xp_amount: int) -> None:
        return None


class FakeLessonRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def mark_completed(self, lesson_id: str) -> None:
        return None


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> None:
        return None


class FakeFourthEstateService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def record(self, *args, **kwargs) -> None:
        return None


class FakeGamificationRepository:
    def __init__(self, db: object) -> None:
        self.db = db


class FakeGamificationService:
    def __init__(self, repository: object) -> None:
        self.repository = repository

    async def get_profile(self, learner_id: str) -> dict[str, Any]:
        return {"learner_id": learner_id, "xp": 20, "level": 1}


async def override_db() -> FakeDB:
    return FakeDB()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload
    return _override


@pytest.fixture(autouse=True)
def gamification_award_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gamification_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(gamification_router, "LessonRepository", FakeLessonRepository)
    monkeypatch.setattr(gamification_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    monkeypatch.setattr(gamification_router, "FourthEstateService", FakeFourthEstateService)
    monkeypatch.setattr(gamification_router, "GamificationRepository", FakeGamificationRepository)
    monkeypatch.setattr(gamification_router, "GamificationServiceV2", FakeGamificationService)
    app.dependency_overrides[gamification_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


def payload(learner_id: str = "learner-1") -> dict[str, Any]:
    return {"learner_id": learner_id, "xp_amount": 10, "event_type": "lesson_completed"}


@pytest.mark.integration
def test_award_xp_allows_admin_write() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user({"sub": "admin-1", "role": "admin"})
    response = TestClient(app).post("/api/v2/gamification/award-xp", json=payload())
    assert response.status_code == 200
    assert "awarded" in str(response.json())


@pytest.mark.integration
def test_award_xp_allows_guardian_with_claim() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user({"sub": "guardian-1", "role": "parent", "guardian_learner_ids": ["learner-1"]})
    response = TestClient(app).post("/api/v2/gamification/award-xp", json=payload())
    assert response.status_code == 200


@pytest.mark.integration
def test_award_xp_allows_learner_self_write() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user({"sub": "learner-1", "role": "student"})
    response = TestClient(app).post("/api/v2/gamification/award-xp", json=payload())
    assert response.status_code == 200


@pytest.mark.integration
def test_award_xp_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user({"sub": "guardian-2", "role": "parent", "guardian_learner_ids": ["other-learner"]})
    response = TestClient(app).post("/api/v2/gamification/award-xp", json=payload())
    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_award_xp_rejects_missing_auth() -> None:
    response = TestClient(app).post("/api/v2/gamification/award-xp", json=payload())
    assert response.status_code == 401


@pytest.mark.integration
def test_award_xp_preserves_not_found() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user({"sub": "admin-1", "role": "admin"})
    response = TestClient(app).post("/api/v2/gamification/award-xp", json=payload("missing-learner"))
    assert response.status_code == 404
