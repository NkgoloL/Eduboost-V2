from __future__ import annotations
from unittest.mock import AsyncMock
import pytest
pytestmark = pytest.mark.integration


from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_deps.auth import AuthContext, TokenType, require_auth_context
from app.api_v2_routers import lessons as lessons_router
from app.core.database import get_db
from app.models import UserRole


def test_lesson_sync_processes_completion_and_feedback(monkeypatch):
    lesson = SimpleNamespace(id="lesson-1", learner_id="learner-1", subject="Mathematics")
    SimpleNamespace(id="learner-1", pseudonym_id="pseudo-1")

    calls: list[tuple[str, str, object]] = []

    class FakeDB:
        async def get(self, _model, record_id):
            if record_id == "lesson-1":
                return lesson
            return None

        async def commit(self):
            return None

    async def override_db():
        yield FakeDB()

    def override_user():
        now = datetime.now(timezone.utc)
        return AuthContext(
            user_id="guardian-1",
            roles=[UserRole.PARENT],
            token_type=TokenType.ACCESS,
            raw_claims={"sub": "guardian-1", "role": "parent"},
            issued_at=now,
            expires_at=now + timedelta(minutes=15),
            jti="lesson-sync-jti",
        )

    class FakeLessonService:
        def __init__(self, _db):
            pass

        async def complete_lesson(self, lesson_id: str) -> None:
            calls.append(("complete", lesson_id, None))

        async def record_feedback(self, lesson_id: str, score: int) -> None:
            calls.append(("feedback", lesson_id, score))

    async def override_lesson_service():
        return FakeLessonService(None)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[require_auth_context] = override_user
    monkeypatch.setattr(
        lessons_router,
        "require_lesson_write_access_for_current_user",
        AsyncMock(return_value=None),
    )
    from app.api_v2_routers.lessons import get_lesson_service
    app.dependency_overrides[get_lesson_service] = override_lesson_service

    client = TestClient(app)
    response = client.post(
        "/api/v2/lessons/sync",
        json={
            "responses": [
                {"lesson_id": "lesson-1", "event_type": "complete"},
                {"lesson_id": "lesson-1", "event_type": "feedback", "score": 5},
            ]
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    # The route returns {"data": {"status": "success", "processed": 2}, ...} due to EnvelopedRoute
    payload = response.json()["data"]
    assert payload["processed"] == 2
    assert ("feedback", "lesson-1", 5) in calls
    assert any(call[0] == "complete" for call in calls)
