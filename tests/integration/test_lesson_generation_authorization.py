from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for lesson generation write authorization."""

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_deps.auth import AuthContext, TokenType
from app.api_v2_routers import lessons as lessons_router
from app.models import UserRole


LEARNER_ID = "11111111-1111-1111-1111-111111111111"
GUARDIAN_ID = "22222222-2222-2222-2222-222222222222"
ADMIN_ID = "33333333-3333-3333-3333-333333333333"


class FakeLessonService:
    async def generate_lesson_for_learner(self, body, user_id: UUID):
        raise AssertionError("background handler should not run during enqueue contract test")


def make_auth_context(payload: dict[str, Any]) -> AuthContext:
    now = datetime.now(timezone.utc)
    return AuthContext(
        user_id=str(payload["sub"]),
        guardian_id=payload.get("guardian_id"),
        learner_id=payload.get("learner_id"),
        roles=[UserRole(str(payload["role"]))],
        token_type=TokenType.ACCESS,
        raw_claims=payload,
        issued_at=now,
        expires_at=now + timedelta(minutes=15),
        jti=payload.get("jti", "jti-lesson-1"),
    )


async def fake_lesson_service():
    return FakeLessonService()


async def fake_enqueue_job(background_tasks, *, operation: str, payload: dict, handler):
    return {
        "job_id": "job-lesson-1",
        "operation": operation,
        "status": "queued",
        "payload": payload,
    }


def override_user(payload: dict[str, Any]):
    async def _override() -> AuthContext:
        return make_auth_context(payload)

    return _override


@pytest.fixture(autouse=True)
def lesson_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(lessons_router, "enqueue_job", fake_enqueue_job)
    monkeypatch.setattr(
        lessons_router,
        "require_active_consent_for_current_user",
        AsyncMock(return_value=None),
    )
    app.dependency_overrides[lessons_router.get_lesson_service] = fake_lesson_service
    yield
    app.dependency_overrides.clear()


def lesson_payload(learner_id: str = LEARNER_ID) -> dict[str, Any]:
    return {
        "learner_id": learner_id,
        "subject": "Math",
        "topic": "Fractions",
        "language": "en",
    }


@pytest.mark.integration
def test_generate_lesson_allows_admin_write() -> None:
    app.dependency_overrides[lessons_router.require_auth_context] = override_user(
        {"sub": ADMIN_ID, "role": "admin"}
    )

    response = TestClient(app).post("/api/v2/lessons/generate", json=lesson_payload())

    assert response.status_code == 202
    body = response.json()
    payload = body.get("data") if isinstance(body, dict) and "data" in body else body
    assert payload["job_id"] == "job-lesson-1"


@pytest.mark.integration
def test_generate_lesson_allows_guardian_with_learner_claim() -> None:
    app.dependency_overrides[lessons_router.require_auth_context] = override_user(
        {"sub": GUARDIAN_ID, "role": "parent", "guardian_learner_ids": [LEARNER_ID]}
    )

    response = TestClient(app).post("/api/v2/lessons/generate", json=lesson_payload())

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_lesson_allows_root_alias() -> None:
    app.dependency_overrides[lessons_router.require_auth_context] = override_user(
        {"sub": GUARDIAN_ID, "role": "parent", "guardian_learner_ids": [LEARNER_ID]}
    )

    response = TestClient(app).post("/api/v2/lessons/", json=lesson_payload())

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_lesson_allows_learner_self_write() -> None:
    app.dependency_overrides[lessons_router.require_auth_context] = override_user(
        {"sub": LEARNER_ID, "role": "student"}
    )

    response = TestClient(app).post("/api/v2/lessons/generate", json=lesson_payload())

    assert response.status_code == 202


@pytest.mark.integration
def test_generate_lesson_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[lessons_router.require_auth_context] = override_user(
        {"sub": GUARDIAN_ID, "role": "parent", "guardian_learner_ids": ["other-learner"]}
    )

    response = TestClient(app).post("/api/v2/lessons/generate", json=lesson_payload())

    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_generate_lesson_rejects_missing_auth() -> None:
    response = TestClient(app).post("/api/v2/lessons/generate", json=lesson_payload())

    assert response.status_code == 401
