import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_factory import (
    router,
    get_content_generation_run_service,
    get_content_generation_executor,
)
from app.api_v2_deps.auth import require_admin, require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_content_factory_runs_and_execution():
    app = FastAPI()
    app.include_router(router)

    mock_run_service = AsyncMock()
    mock_run_service.list_runs.return_value = []
    mock_run_service.get_run.side_effect = LookupError("Run not found")

    mock_executor = AsyncMock()
    mock_executor.execute_run.side_effect = LookupError("Run execution not found")

    auth_ctx = MagicMock()
    auth_ctx.user_id = "adm-1"

    app.dependency_overrides[require_admin] = lambda: {"role": "admin"}
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_content_generation_run_service] = lambda: mock_run_service
    app.dependency_overrides[get_content_generation_executor] = lambda: mock_executor
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_list = await client.get("/admin/content-factory/runs")
        assert resp_list.status_code == 200
        assert resp_list.json() == []

        fake_id = uuid.uuid4()
        resp_get = await client.get(f"/admin/content-factory/runs/{fake_id}")
        assert resp_get.status_code == 404

        resp_exec = await client.post(f"/admin/content-factory/runs/{fake_id}/execute")
        assert resp_exec.status_code == 404
