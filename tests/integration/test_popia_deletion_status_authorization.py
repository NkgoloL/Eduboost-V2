from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for POPIA deletion-status authorization."""

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import popia as popia_router
from app.core.security import get_current_user


class FakeLearnerRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_by_id(self, learner_id: str) -> SimpleNamespace | None:
        if learner_id == "missing-learner":
            return None
        deletion_requested_at = datetime(2026, 1, 1, tzinfo=UTC) if learner_id == "pending-learner" else None
        return SimpleNamespace(
            id=learner_id,
            guardian_id="guardian-1",
            deletion_requested_at=deletion_requested_at,
            is_deleted=False,
        )


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def popia_deletion_status_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(popia_router, "LearnerRepository", FakeLearnerRepository)
    app.dependency_overrides[get_current_user] = override_user({"sub": "none"})
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_popia_deletion_status_allows_admin_read() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/popia/deletion-status/learner-1")

    assert response.status_code == 200
    assert "deletion_pending" in response.json()["data"]


@pytest.mark.integration
def test_popia_deletion_status_allows_guardian_read() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/popia/deletion-status/learner-1")

    assert response.status_code == 200


@pytest.mark.integration
def test_popia_deletion_status_allows_learner_self_read() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )

    response = TestClient(app).get("/api/v2/popia/deletion-status/learner-1")

    assert response.status_code == 200


@pytest.mark.integration
def test_popia_deletion_status_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/popia/deletion-status/learner-1")

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json()["error"])


@pytest.mark.integration
def test_popia_deletion_status_rejects_missing_auth() -> None:
    response = TestClient(app).get("/api/v2/popia/deletion-status/learner-1")

    assert response.status_code == 401


@pytest.mark.integration
def test_popia_deletion_status_preserves_not_found() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/popia/deletion-status/missing-learner")

    assert response.status_code == 404
