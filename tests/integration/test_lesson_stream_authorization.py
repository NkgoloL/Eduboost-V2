from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

"""HTTP contract tests for lesson stream write authorization."""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import lessons as lessons_router


LEARNER_ID = "11111111-1111-1111-1111-111111111111"
GUARDIAN_ID = "22222222-2222-2222-2222-222222222222"
ADMIN_ID = "33333333-3333-3333-3333-333333333333"


class FakeLesson:
    def model_dump_json(self) -> str:
        return '{"lesson_id":"lesson-1"}'


class FakeLessonService:
    async def generate_lesson_for_learner(self, body, user_id):
        return FakeLesson(), False, "fake"


async def fake_lesson_service():
    return FakeLessonService()


def override_user(payload: dict[str, Any]):
    async def _override() -> dict[str, Any]:
        return payload
    return _override


@pytest.fixture(autouse=True)
def lesson_stream_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        lessons_router,
        "require_active_consent_for_current_user",
        AsyncMock(return_value=None),
    )
    app.dependency_overrides[lessons_router.get_lesson_service] = fake_lesson_service
    yield
    app.dependency_overrides.clear()


def payload(learner_id: str = LEARNER_ID) -> dict[str, Any]:
    return {"learner_id": learner_id, "subject": "Math", "topic": "Fractions", "language": "en"}


@pytest.mark.integration
def test_lesson_stream_allows_admin_write() -> None:
    app.dependency_overrides[lessons_router.get_current_user] = override_user({"sub": ADMIN_ID, "role": "admin"})
    response = TestClient(app).post("/api/v2/lessons/generate/stream", json=payload())
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


@pytest.mark.integration
def test_lesson_stream_allows_guardian_with_claim() -> None:
    app.dependency_overrides[lessons_router.get_current_user] = override_user({"sub": GUARDIAN_ID, "role": "parent", "guardian_learner_ids": [LEARNER_ID]})
    response = TestClient(app).post("/api/v2/lessons/generate/stream", json=payload())
    assert response.status_code == 200


@pytest.mark.integration
def test_lesson_stream_allows_learner_self_write() -> None:
    app.dependency_overrides[lessons_router.get_current_user] = override_user({"sub": LEARNER_ID, "role": "student"})
    response = TestClient(app).post("/api/v2/lessons/generate/stream", json=payload())
    assert response.status_code == 200


@pytest.mark.integration
def test_lesson_stream_rejects_unrelated_guardian() -> None:
    app.dependency_overrides[lessons_router.get_current_user] = override_user({"sub": GUARDIAN_ID, "role": "parent", "guardian_learner_ids": ["other-learner"]})
    response = TestClient(app).post("/api/v2/lessons/generate/stream", json=payload())
    assert response.status_code == 403
    assert "object_forbidden" in str(response.json())


@pytest.mark.integration
def test_lesson_stream_rejects_missing_auth() -> None:
    response = TestClient(app).post("/api/v2/lessons/generate/stream", json=payload())
    assert response.status_code == 401
