import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.onboarding import router
from app.api_v2_deps.auth import require_auth_context


@pytest.mark.asyncio
async def test_onboarding_questions_route():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-test"
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/onboarding/questions")
        assert resp.status_code == 200
        data = resp.json()
        questions = data.get("data") if "data" in data else data
        assert isinstance(questions, list)
        assert len(questions) > 0
