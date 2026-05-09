"""HTTP contract tests for consent-revoke authorization."""
from __future__ import annotations

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

    async def revoke(self, learner_id: str, guardian_id: str, reason: str) -> None:
        return None


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def consent_revoke_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(consent_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(consent_router, "ConsentService", FakeConsentService)
    app.dependency_overrides[consent_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


def payload(learner_id: str = LEARNER_ID) -> dict[str, str]:
    return {"learner_id": learner_id, "reason": "guardian_request"}


@pytest.mark.integration
def test_consent_revoke_allows_admin_write() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).post("/api/v2/consent/revoke", json=payload())

    assert response.status_code == 200
    assert "revoked" in str(response.json())


@pytest.mark.integration
def test_consent_revoke_allows_guardian_with_claim() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent", "guardian_learner_ids": [LEARNER_ID]}
    )

    response = TestClient(app).post("/api/v2/consent/revoke", json=payload())

    assert response.status_code == 200


@pytest.mark.integration
def test_consent_revoke_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent", "guardian_learner_ids": ["other-learner"]}
    )

    response = TestClient(app).post("/api/v2/consent/revoke", json=payload())

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_consent_revoke_rejects_missing_auth() -> None:
    response = TestClient(app).post("/api/v2/consent/revoke", json=payload())

    assert response.status_code == 401


@pytest.mark.integration
def test_consent_revoke_preserves_not_found() -> None:
    app.dependency_overrides[consent_router.get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).post("/api/v2/consent/revoke", json=payload(MISSING_ID))

    assert response.status_code == 404
