from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for consent-status authorization."""

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import consent as consent_router


LEARNER_ID = "11111111-1111-1111-1111-111111111111"
MISSING_ID = "99999999-9999-9999-9999-999999999999"


class FakeLearnerRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_by_id(self, learner_id: str) -> SimpleNamespace | None:
        if learner_id == MISSING_ID:
            return None
        return SimpleNamespace(id=learner_id, guardian_id="guardian-1")


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_status(self, learner_id: str):
        return SimpleNamespace(
            granted_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            expires_at=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def consent_status_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(consent_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(consent_router, "ConsentService", FakeConsentService)
    app.dependency_overrides[consent_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_consent_status_allows_admin_read() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get(f"/api/v2/consent/status/{LEARNER_ID}")

    assert response.status_code == 200
    body = response.json()
    payload = body.get("data") if "data" in body else body
    assert "active" in payload


@pytest.mark.integration
def test_consent_status_allows_guardian_read() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )

    response = TestClient(app).get(f"/api/v2/consent/status/{LEARNER_ID}")

    assert response.status_code == 200


@pytest.mark.integration
def test_consent_status_allows_learner_self_read() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": LEARNER_ID, "role": "student"}
    )

    response = TestClient(app).get(f"/api/v2/consent/status/{LEARNER_ID}")

    assert response.status_code == 200


@pytest.mark.integration
def test_consent_status_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )

    response = TestClient(app).get(f"/api/v2/consent/status/{LEARNER_ID}")

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_consent_status_rejects_missing_auth() -> None:
    response = TestClient(app).get(f"/api/v2/consent/status/{LEARNER_ID}")

    assert response.status_code == 401


@pytest.mark.integration
def test_consent_status_preserves_not_found() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get(f"/api/v2/consent/status/{MISSING_ID}")

    assert response.status_code == 404
