import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.tutor import router, get_tutor_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db
from app.core.rate_limit import limiter


@pytest.mark.asyncio
async def test_stream_tutor_reply_success_and_error_routes(monkeypatch):
    monkeypatch.setattr(limiter, "enabled", False)

    app = FastAPI()
    app.state.limiter = limiter
    app.include_router(router)

    user_id = uuid.uuid4()
    learner_id = "learner-123"
    lesson_id = "lesson-456"
    session_id = uuid.uuid4()
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

    assistant_msg = MagicMock()
    assistant_msg.message_id = assistant_msg_id
    assistant_msg.role = "assistant"
    assistant_msg.content = "Great job with math! Keep going."
    assistant_msg.safety_status = "safe"
    assistant_msg.quality_score = 0.99
    assistant_msg.provider = "mock_llm"
    assistant_msg.created_at = now

    mock_service.ask.return_value = {
        "learner": MagicMock(),
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
                "text": "Can you explain fractions?",
                "client_message_id": "client-msg-stream-1",
            }
            response = await client.post(f"/tutor/sessions/{session_id}/messages/stream", json=payload)
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            content = response.text
            assert "event: status" in content
            assert "event: token" in content
            assert "event: done" in content

            # Test exception branch yielding event: error
            mock_service.ask.side_effect = HTTPException(status_code=503, detail="Service Unavailable")
            response_err = await client.post(f"/tutor/sessions/{session_id}/messages/stream", json=payload)
            assert response_err.status_code == 200
            content_err = response_err.text
            assert "event: error" in content_err
            assert "Service Unavailable" in content_err
