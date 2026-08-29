from datetime import datetime, timezone
from decimal import Decimal
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.ai_operations import router
from app.api_v2_deps.auth import require_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_ai_operations_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "admin-user"
    auth_ctx.roles = ["admin"]

    session = AsyncMock()
    session.scalars = AsyncMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    session.scalars.return_value = scalars_mock

    app.dependency_overrides[require_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.ai_operations.AIOperationsService") as MockService:
        mock_instance = MagicMock()
        mock_instance.counter_view = AsyncMock(
            return_value={
                "scope_type": "user",
                "scope_id": "usr-123",
                "period_key": "2026-08",
                "used_tokens": 100,
                "reserved_tokens": 10,
                "token_limit": 1000,
                "remaining_tokens": 890,
                "used_cost_usd": Decimal("0.05"),
                "alert_threshold_reached": False,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        mock_instance.provider_health = AsyncMock(return_value=[])
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_user_budget = await client.get("/admin/ai-operations/budgets/users/usr-123")
            assert resp_user_budget.status_code == 200

            resp_health = await client.get("/admin/ai-operations/providers/health")
            assert resp_health.status_code == 200

            resp_usage = await client.get("/admin/ai-operations/usage")
            assert resp_usage.status_code == 200

            resp_res = await client.get("/admin/ai-operations/reservations")
            assert resp_res.status_code == 200
