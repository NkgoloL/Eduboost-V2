import datetime
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.tutor import router, get_tutor_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_tutor_get_session_and_messages():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    session_id = uuid.uuid4()
    learner_id = "00000000-0000-0000-0000-000000000002"
    lesson_id = "00000000-0000-0000-0000-000000000003"

    mock_session_obj = MagicMock()
    mock_session_obj.session_id = session_id
    mock_session_obj.learner_id = learner_id
    mock_session_obj.lesson_id = lesson_id
    mock_session_obj.language = "en"
    mock_session_obj.status = "active"

    mock_db = AsyncMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    mock_db.scalars = AsyncMock(return_value=scalars_mock)

    mock_service = MagicMock()
    mock_service.get_session = AsyncMock(return_value=mock_session_obj)

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_tutor_service] = lambda: mock_service

    with patch("app.api_v2_routers.tutor.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.tutor.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.tutor.require_lesson_read_access_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.tutor.serialize_session") as mock_serialize:

        now = datetime.datetime.now(datetime.timezone.utc)
        mock_serialize.return_value = {
            "session_id": session_id,
            "learner_id": learner_id,
            "lesson_id": lesson_id,
            "language": "en",
            "status": "active",
            "message_count": 0,
            "escalation_count": 0,
            "created_at": now,
            "last_activity_at": now,
            "messages": [],
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_get = await client.get(f"/tutor/sessions/{session_id}")
            assert resp_get.status_code == 200
            data = resp_get.json()
            payload = data.get("data") if "data" in data else data
            assert payload["session_id"] == str(session_id)
            assert payload["status"] == "active"
