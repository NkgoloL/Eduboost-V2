from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for POPIA correction-request authorization."""

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import popia as popia_router
from app.core.security import get_current_user


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
        return SimpleNamespace(id=learner_id, guardian_id="guardian-1")


class FakePOPIADataRightsService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def request_correction(self, learner_id: str, current_user: dict, fields: dict, reason: str) -> dict:
        return {"learner_id": learner_id, "status": "corrected", "fields": fields, "reason": reason}


async def override_db() -> FakeDB:
    return FakeDB()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload

    return _override


@pytest.fixture(autouse=True)
def popia_correction_request_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(popia_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(popia_router, "POPIADataRightsService", FakePOPIADataRightsService)
    app.dependency_overrides[popia_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


def correction_payload() -> dict[str, Any]:
    return {"fields": {"display_name": "Updated Learner"}, "reason": "correct inaccurate profile"}


@pytest.mark.integration
def test_popia_correction_request_allows_admin_write() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).post(
        "/api/v2/popia/correction-request/learner-1",
        json=correction_payload(),
    )

    assert response.status_code == 200
    assert "corrected" in str(response.json()["data"])


@pytest.mark.integration
def test_popia_correction_request_allows_guardian_with_claim() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "guardian-1", "role": "parent", "guardian_learner_ids": ["learner-1"]}
    )

    response = TestClient(app).post(
        "/api/v2/popia/correction-request/learner-1",
        json=correction_payload(),
    )

    assert response.status_code == 200


@pytest.mark.integration
def test_popia_correction_request_allows_learner_self_write() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "learner-1", "role": "student"}
    )

    response = TestClient(app).post(
        "/api/v2/popia/correction-request/learner-1",
        json=correction_payload(),
    )

    assert response.status_code == 200


@pytest.mark.integration
def test_popia_correction_request_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "guardian-2", "role": "parent", "guardian_learner_ids": ["learner-2"]}
    )

    response = TestClient(app).post(
        "/api/v2/popia/correction-request/learner-1",
        json=correction_payload(),
    )

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json()["error"])


@pytest.mark.integration
def test_popia_correction_request_rejects_missing_auth() -> None:
    response = TestClient(app).post(
        "/api/v2/popia/correction-request/learner-1",
        json=correction_payload(),
    )

    assert response.status_code == 401


@pytest.mark.integration
def test_popia_correction_request_preserves_not_found() -> None:
    app.dependency_overrides[get_current_user] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).post(
        "/api/v2/popia/correction-request/missing-learner",
        json=correction_payload(),
    )

    assert response.status_code == 404
