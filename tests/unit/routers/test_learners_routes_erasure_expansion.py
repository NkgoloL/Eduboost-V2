import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.learners import router, enqueue_data_purge
from app.api_v2_deps.auth import require_parent_or_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_enqueue_data_purge_helper():
    await enqueue_data_purge("lrn-1", "pseudo-1")


@pytest.mark.asyncio
async def test_request_erasure_endpoint():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    session = AsyncMock()

    app.dependency_overrides[require_parent_or_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.learners.POPIADataRightsService") as MockService:
        mock_instance = AsyncMock()
        mock_instance.request_erasure.return_value = {"status": "pending", "request_id": "req-1"}
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.delete("/learners/lrn-1")
            assert resp.status_code == 202
            data = resp.json()
            assert (data.get("data") or data).get("status") == "pending"
