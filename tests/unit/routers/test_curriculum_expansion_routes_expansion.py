import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.curriculum_expansion import router
from app.api_v2_deps.auth import require_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_curriculum_expansion_coverage_route():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "admin-usr"
    auth_ctx.roles = ["admin"]

    session = AsyncMock()

    app.dependency_overrides[require_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.curriculum_expansion.CurriculumExpansionService") as MockService:
        mock_instance = MagicMock()
        mock_instance.coverage_for_scope = AsyncMock(
            return_value={
                "scope_id": "math-g4",
                "target_total": 50,
                "approved_total": 45,
                "published_total": 40,
                "gap_count": 10,
                "coverage_pct": 80.0,
            }
        )
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/admin/curriculum-expansion/coverage/math-g4")
            assert resp.status_code == 200
            data = resp.json()
            payload = data.get("data") if "data" in data else data
            assert payload["scope_id"] == "math-g4"
            assert payload["coverage_pct"] == 80.0
