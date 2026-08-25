from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for parent access-bundle export authorization."""

from types import SimpleNamespace  # noqa: E402
from typing import Any  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api_v2_deps.auth import AuthContext, TokenType, require_parent_or_admin  # noqa: E402
from app.api_v2 import app  # noqa: E402
from app.api_v2_routers import parents as parents_router  # noqa: E402
from app.models import UserRole  # noqa: E402


class FakeDB:
    async def get(self, model, key):
        if key == "missing-guardian":
            return None
        return SimpleNamespace(id=key, subscription_tier="free")

    async def commit(self) -> None:
        return None

    def expire_all(self) -> None:
        return None


class FakeLearnerRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_by_guardian(self, guardian_id: str) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                id="learner-1",
                guardian_id=guardian_id,
                display_name="Pilot Learner",
            )
        ]


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> None:
        return None


async def override_db() -> FakeDB:
    return FakeDB()


def _auth_context(payload: dict[str, Any]) -> AuthContext:
    return AuthContext(
        user_id=payload["sub"],
        roles=[UserRole(payload["role"])],
        token_type=TokenType.ACCESS,
        raw_claims=payload,
        jti="test-jti",
    )


def override_user(payload: dict[str, Any]):
    async def _override() -> AuthContext:
        return _auth_context(payload)

    return _override


@pytest.fixture(autouse=True)
def parent_export_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(parents_router, "LearnerRepository", FakeLearnerRepository)
    monkeypatch.setattr(parents_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    app.dependency_overrides[parents_router.get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_parent_export_allows_self_guardian() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "guardian-1", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/parents/guardian-1/export")

    assert response.status_code == 200
    body = response.json()
    assert "exports" in str(body["data"])


@pytest.mark.integration
def test_parent_export_allows_admin_for_any_guardian() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/parents/guardian-1/export")

    assert response.status_code == 200


@pytest.mark.integration
def test_parent_export_rejects_other_guardian() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "guardian-2", "role": "parent"}
    )

    response = TestClient(app).get("/api/v2/parents/guardian-1/export")

    assert response.status_code == 403


@pytest.mark.integration
def test_parent_export_rejects_missing_auth() -> None:
    response = TestClient(app).get("/api/v2/parents/guardian-1/export")

    assert response.status_code == 401


@pytest.mark.integration
def test_parent_export_preserves_guardian_not_found() -> None:
    app.dependency_overrides[require_parent_or_admin] = override_user(
        {"sub": "admin-1", "role": "admin"}
    )

    response = TestClient(app).get("/api/v2/parents/missing-guardian/export")

    assert response.status_code == 404
