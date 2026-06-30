from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for gamification profile read authorization."""

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import gamification as gamification_router


class FakeLearnerRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_by_id(self, learner_id: str) -> SimpleNamespace | None:
        if learner_id == "missing-learner":
            return None
        return SimpleNamespace(id=learner_id, guardian_id="guardian-1")


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> None:
        return None


class FakeGamificationService:
    def __init__(self, repository: object) -> None:
        self.repository = repository

    async def get_profile(self, learner_id: str) -> dict[str, Any]:
        return {"learner_id": learner_id, "xp": 10, "level": 1}


class FakeGamificationRepository:
    def __init__(self, db: object) -> None:
        self.db = db


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def gamification_profile_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gamification_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(gamification_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    monkeypatch.setattr(gamification_router, "GamificationServiceV2", FakeGamificationService)
    monkeypatch.setattr(gamification_router, "GamificationRepository", FakeGamificationRepository)
    app.dependency_overrides[gamification_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_gamification_profile_allows_admin_read() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/gamification/profile/learner-1")

    assert response.status_code == 200
    assert "learner-1" in str(response.json())


@pytest.mark.integration
def test_gamification_profile_allows_guardian_read() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/gamification/profile/learner-1")

    assert response.status_code == 200


@pytest.mark.integration
def test_gamification_profile_allows_learner_self_read() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )

    response = TestClient(app).get("/api/v2/gamification/profile/learner-1")

    assert response.status_code == 200


@pytest.mark.integration
def test_gamification_profile_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/gamification/profile/learner-1")

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_gamification_profile_rejects_missing_auth() -> None:
    response = TestClient(app).get("/api/v2/gamification/profile/learner-1")

    assert response.status_code == 401


@pytest.mark.integration
def test_gamification_profile_preserves_not_found() -> None:
    app.dependency_overrides[gamification_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/gamification/profile/missing-learner")

    assert response.status_code == 404
