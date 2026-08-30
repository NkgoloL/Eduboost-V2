import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.tutor import router, get_tutor_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_tutor_cancel_session_and_access_route():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    session_id = uuid.uuid4()
    learner_id = "00000000-0000-0000-0000-000000000002"
    lesson_id = "00000000-0000-0000-0000-000000000003"

    mock_session = MagicMock()
    mock_session.session_id = session_id
    mock_session.learner_id = learner_id
    mock_session.lesson_id = lesson_id

    mock_db = AsyncMock()
    mock_service = MagicMock()
    mock_service.get_session = AsyncMock(return_value=mock_session)
    mock_service.cancel_session = AsyncMock(return_value=True)

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_tutor_service] = lambda: mock_service

    with patch("app.api_v2_routers.tutor.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.tutor.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.tutor.require_lesson_read_access_for_current_user", new=AsyncMock()):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_cancel = await client.post(f"/tutor/sessions/{session_id}/cancel")
            assert resp_cancel.status_code == 200
            data_cancel = resp_cancel.json()
            payload = data_cancel.get("data") if "data" in data_cancel else data_cancel
            assert payload["session_id"] == str(session_id)
            assert payload["status"] == "cancelled"
