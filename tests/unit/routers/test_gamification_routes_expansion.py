import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.gamification import router
from app.core.database import get_db


@pytest.mark.asyncio
async def test_get_leaderboard_endpoint():
    app = FastAPI()
    app.include_router(router)

    session = AsyncMock()

    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.gamification.GamificationServiceV2") as MockService:
        mock_instance = AsyncMock()
        mock_instance.leaderboard.return_value = [{"rank": 1, "pseudonym": "Learner-1", "xp": 100}]
        MockService.from_session.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/gamification/leaderboard?limit=5")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data.get("data") or data) == 1
            assert (data.get("data") or data)[0]["rank"] == 1
