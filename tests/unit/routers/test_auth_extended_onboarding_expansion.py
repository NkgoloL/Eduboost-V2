import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.auth_extended import (
    router,
    VALID_ONBOARDING_STEPS,
)
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


def test_valid_onboarding_steps():
    assert "email_verified" in VALID_ONBOARDING_STEPS
    assert "profile_complete" in VALID_ONBOARDING_STEPS
    assert "guardian_consent" in VALID_ONBOARDING_STEPS
    assert "diagnostic_done" in VALID_ONBOARDING_STEPS
    assert "plan_accepted" in VALID_ONBOARDING_STEPS


@pytest.mark.asyncio
async def test_get_onboarding_existing():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"
    auth_ctx.raw_claims = {"email_verified": True}

    mock_state = MagicMock()
    mock_state.to_dict.return_value = {
        "user_id": "user-123",
        "email_verified": True,
        "profile_complete": False,
        "is_complete": False,
    }

    session = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_state
    session.execute.return_value = mock_res

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/auth/onboarding")
        assert resp.status_code == 200
        assert resp.json()["user_id"] == "user-123"
        assert resp.json()["email_verified"] is True
