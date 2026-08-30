import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_review import (
    router,
    get_review_actor,
    get_governance_service,
    ReviewActor,
)
from app.core.database import get_db


@pytest.mark.asyncio
async def test_get_review_history_endpoint():
    app = FastAPI()
    app.include_router(router)

    actor = ReviewActor(
        user_id="actor-1",
        permissions=frozenset({"history_read", "stale_read"}),
        competencies=("caps",),
    )

    mock_gov = AsyncMock()
    mock_gov.list_history.return_value = {"decisions": [], "transitions": []}
    mock_gov.list_stale_assignments.return_value = []

    session = AsyncMock()

    app.dependency_overrides[get_review_actor] = lambda: actor
    app.dependency_overrides[get_governance_service] = lambda: mock_gov
    app.dependency_overrides[get_db] = lambda: session

    art_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # History
        resp_hist = await client.get(f"/content-review/artifacts/{art_id}/history")
        assert resp_hist.status_code == 200
        data_hist = resp_hist.json()
        assert (data_hist.get("data") or data_hist).get("decisions") == []
        assert (data_hist.get("data") or data_hist).get("transitions") == []

        # Stale assignments
        resp_stale = await client.get("/content-review/assignments/stale")
        assert resp_stale.status_code == 200
        data_stale = resp_stale.json()
        assert (data_stale.get("data") if isinstance(data_stale, dict) and "data" in data_stale else data_stale) == []
