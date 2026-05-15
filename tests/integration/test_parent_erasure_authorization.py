from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for parent learner-erasure authorization."""

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import parents as parents_router
from app.core.security import require_parent_or_admin


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
        return SimpleNamespace(
            id=learner_id,
            guardian_id="guardian-1",
            pseudonym_id=f"pseudo-{learner_id}",
        )

    async def soft_delete(self, learner_id: str) -> None:
        return None


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def execute_erasure(self, actor_id: str, learner_id: str) -> None:
        return None


class FakeFourthEstateService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def record(self, *args, **kwargs) -> None:
        return None


async def override_db() -> FakeDB:
    return FakeDB()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def parent_erasure_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(parents_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(parents_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    monkeypatch.setattr(parents_router, "FourthEstateService", FakeFourthEstateService)
    monkeypatch.setattr(parents_router, "ConsentService", FakeConsentService)
    app.dependency_overrides[parents_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_parent_erasure_allows_admin_write() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).delete("/api/v2/parents/learners/learner-1")

    assert response.status_code == 204


@pytest.mark.integration
def test_parent_erasure_allows_guardian_with_claim() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "guardian-1", "role": "parent", "guardian_learner_ids": ["learner-1"]}
    )

    response = TestClient(app).delete("/api/v2/parents/learners/learner-1")

    assert response.status_code == 204


@pytest.mark.integration
def test_parent_erasure_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "guardian-2", "role": "parent", "guardian_learner_ids": ["learner-2"]}
    )

    response = TestClient(app).delete("/api/v2/parents/learners/learner-1")

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_parent_erasure_rejects_missing_auth() -> None:
    response = TestClient(app).delete("/api/v2/parents/learners/learner-1")

    assert response.status_code == 401


@pytest.mark.integration
def test_parent_erasure_preserves_not_found() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).delete("/api/v2/parents/learners/missing-learner")

    assert response.status_code == 404
