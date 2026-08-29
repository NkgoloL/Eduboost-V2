import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.tutor import (
    router,
    get_tutor_service,
    _require_session_access,
)
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_tutor_cancel_session_endpoint():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    mock_service = AsyncMock()
    mock_service.cancel_session.return_value = None

    session_id = uuid.uuid4()
    mock_sess = MagicMock()
    mock_sess.session_id = session_id
    mock_sess.learner_id = uuid.uuid4()
    mock_sess.lesson_id = uuid.uuid4()
    mock_service.get_session.return_value = mock_sess

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_tutor_service] = lambda: mock_service
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.tutor.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.tutor.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.tutor.require_lesson_read_access_for_current_user", new=AsyncMock()):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(f"/tutor/sessions/{session_id}/cancel")
            assert resp.status_code == 200
            data = resp.json()
            assert (data.get("data") or data).get("status") == "cancelled"
            assert (data.get("data") or data).get("session_id") == str(session_id)
