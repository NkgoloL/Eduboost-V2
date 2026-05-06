from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core.database import get_db
from app.core.security import get_current_user


def test_lesson_sync_processes_completion_and_feedback(monkeypatch):
    lesson = SimpleNamespace(id="lesson-1", learner_id="learner-1", subject="Mathematics")
    learner = SimpleNamespace(id="learner-1", pseudonym_id="pseudo-1")

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
        return {"sub": "guardian-1", "role": "parent"}

    class FakeConsentService:
        def __init__(self, _db):
            pass

        async def require_active_consent(self, _learner_id, actor_id=None):
            return None

    class FakeLessonRepository:
        def __init__(self, _db):
            pass

        async def mark_completed(self, lesson_id, completed_at=None):
            calls.append(("complete", lesson_id, completed_at))

        async def record_feedback(self, lesson_id, score):
            calls.append(("feedback", lesson_id, score))

    class FakeLearnerRepository:
        def __init__(self, _db):
            pass

        async def get_by_id(self, _learner_id):
            return learner

    monkeypatch.setattr("app.api_v2_routers.lessons.ConsentService", FakeConsentService)
    monkeypatch.setattr("app.api_v2_routers.lessons.LessonRepository", FakeLessonRepository)
    monkeypatch.setattr("app.api_v2_routers.lessons.LearnerRepository", FakeLearnerRepository)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as client:
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
    assert response.json()["processed"] == 2
    assert ("feedback", "lesson-1", 5) in calls
    assert any(call[0] == "complete" for call in calls)

