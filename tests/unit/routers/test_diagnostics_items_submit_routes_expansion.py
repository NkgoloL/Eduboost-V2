import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.diagnostics import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_diagnostics_items_and_submit_404_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "parent-usr"
    auth_ctx.roles = ["parent"]

    session = AsyncMock()
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.diagnostics.diagnostic_repositories.learner") as mock_learner_repo:
        repo_inst = MagicMock()
        repo_inst.get_by_id = AsyncMock(return_value=None)
        mock_learner_repo.return_value = repo_inst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Test get items 404
            resp_items_404 = await client.get("/diagnostics/items/lrn-nonexistent")
            assert resp_items_404.status_code == 404
            assert "Learner not found" in resp_items_404.json()["detail"]

            # 2. Test submit diagnostic 404
            resp_sub_404 = await client.post(
                "/diagnostics/submit",
                json={
                    "learner_id": "lrn-nonexistent",
                    "answers": [{"item_id": "itm-1", "selected_option": "A"}],
                },
            )
            assert resp_sub_404.status_code == 404
            assert "Learner not found" in resp_sub_404.json()["detail"]
