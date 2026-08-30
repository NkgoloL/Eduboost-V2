import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.auth_extended import (
    router,
    _current_user_id,
    _grade_to_int,
)
from app.api_v2_deps.auth import AuthContext
from app.core.database import get_db


def test_auth_extended_helpers():
    assert _grade_to_int("R") == 0
    assert _grade_to_int("5") == 5

    ctx = AuthContext(
        user_id="user-123",
        roles=["parent"],
        token_type="access",
        jti="jti-123",
        raw_claims={},
    )
    assert _current_user_id(ctx) == "user-123"
    assert _current_user_id({"sub": "user-456"}) == "user-456"


@pytest.mark.asyncio
async def test_forgot_password_flow():
    app = FastAPI()
    app.include_router(router)

    session = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_res

    app.dependency_overrides[get_db] = lambda: session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/auth/forgot-password", json={"email": "nonexistent@test.com"})
        assert resp.status_code == 202
        assert "If that email exists" in resp.json()["detail"]
