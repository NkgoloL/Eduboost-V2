import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.tutor import router, get_tutor_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db
from app.core.rate_limit import limiter


@pytest.mark.asyncio
async def test_ask_tutor_message_success_route(monkeypatch):
    monkeypatch.setattr(limiter, "enabled", False)

    app = FastAPI()
    app.state.limiter = limiter
    app.include_router(router)

    user_id = uuid.uuid4()
    learner_id = "learner-123"
    lesson_id = "lesson-456"
    session_id = uuid.uuid4()
    learner_msg_id = uuid.uuid4()
    assistant_msg_id = uuid.uuid4()
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

    mock_service.get_session.return_value = mock_session

    learner_msg = MagicMock()
    learner_msg.message_id = learner_msg_id
    learner_msg.role = "learner"
    learner_msg.content = "What is 2 + 2?"
    learner_msg.safety_status = "safe"
    learner_msg.quality_score = 1.0
    learner_msg.provider = None
    learner_msg.created_at = now

    assistant_msg = MagicMock()
    assistant_msg.message_id = assistant_msg_id
    assistant_msg.role = "assistant"
    assistant_msg.content = "2 + 2 equals 4!"
    assistant_msg.safety_status = "safe"
    assistant_msg.quality_score = 0.98
    assistant_msg.provider = "mock_llm"
    assistant_msg.created_at = now

    mock_service.ask.return_value = {
        "learner": learner_msg,
        "assistant": assistant_msg,
        "fallback": False,
        "escalation": False,
    }

    app.dependency_overrides[require_auth_context] = lambda: mock_auth
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_tutor_service] = lambda: mock_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("app.api_v2_routers.tutor.require_learner_write_for_current_user"), \
             patch("app.api_v2_routers.tutor.require_active_consent_for_current_user", new_callable=AsyncMock), \
             patch("app.api_v2_routers.tutor.require_lesson_read_access_for_current_user", new_callable=AsyncMock):
            payload = {
                "text": "What is 2 + 2?",
                "client_message_id": "client-msg-12345",
            }
            response = await client.post(f"/tutor/sessions/{session_id}/messages", json=payload)
            assert response.status_code == 200
            data = response.json()
            actual_data = data.get("data", data)
            assert actual_data["session_id"] == str(session_id)
            assert actual_data["learner_message"]["content"] == "What is 2 + 2?"
            assert actual_data["assistant_message"]["content"] == "2 + 2 equals 4!"
            assert actual_data["fallback"] is False
            assert actual_data["escalation_created"] is False
