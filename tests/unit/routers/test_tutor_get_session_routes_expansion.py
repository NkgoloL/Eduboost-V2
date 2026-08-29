import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.tutor import router, get_tutor_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_tutor_get_session_and_messages_route():
    app = FastAPI()
    app.include_router(router)

    user_id = uuid.uuid4()
    learner_id = "learner-123"
    lesson_id = "lesson-456"
    session_id = uuid.uuid4()
    message_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    mock_auth = MagicMock()
    mock_auth.user_id = str(user_id)
    mock_auth.roles = ["learner"]

    mock_db = AsyncMock()
    mock_service = AsyncMock()

    mock_session = MagicMock()
    mock_session.session_id = session_id
    mock_session.learner_id = learner_id
    mock_session.lesson_id = lesson_id
    mock_session.language = "en"
    mock_session.status = "active"
    mock_session.message_count = 1
    mock_session.escalation_count = 0
    mock_session.created_at = now
    mock_session.last_activity_at = now

    mock_service.get_session.return_value = mock_session

    msg = MagicMock()
    msg.message_id = message_id
    msg.session_id = session_id
    msg.role = "assistant"
    msg.content = "Welcome to tutoring!"
    msg.safety_status = "safe"
    msg.quality_score = 0.95
    msg.provider = "mock"
    msg.created_at = now

    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [msg]
    mock_db.scalars.return_value = scalars_mock

    app.dependency_overrides[require_auth_context] = lambda: mock_auth
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_tutor_service] = lambda: mock_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("app.api_v2_routers.tutor.require_learner_write_for_current_user"), \
             patch("app.api_v2_routers.tutor.require_active_consent_for_current_user", new_callable=AsyncMock), \
             patch("app.api_v2_routers.tutor.require_lesson_read_access_for_current_user", new_callable=AsyncMock):
            response = await client.get(f"/tutor/sessions/{session_id}")
            assert response.status_code == 200
            data = response.json()
            # Enveloped response check
            actual_data = data.get("data", data)
            assert actual_data["session_id"] == str(session_id)
            assert actual_data["learner_id"] == learner_id
            assert len(actual_data["messages"]) == 1
            assert actual_data["messages"][0]["content"] == "Welcome to tutoring!"
