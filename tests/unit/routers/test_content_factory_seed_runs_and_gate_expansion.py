import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_factory import (
    router,
    get_content_staging_seed_executor,
    get_production_promotion_gate,
)
from app.api_v2_deps.auth import require_admin, require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_content_factory_seed_runs_and_production_gate():
    app = FastAPI()
    app.include_router(router)

    mock_seed_executor = AsyncMock()
    mock_seed_page = MagicMock()
    mock_seed_page.items = []
    mock_seed_page.total = 0
    mock_seed_page.limit = 50
    mock_seed_page.offset = 0
    mock_seed_executor.list_seed_runs.return_value = mock_seed_page
    mock_seed_executor.get_seed_run.side_effect = LookupError("Seed run not found")

    mock_gate = AsyncMock()
    mock_gate_report = MagicMock()
    mock_gate_report.scope_id = "scope-1"
    mock_gate_report.status.value = "promotable"
    mock_gate_report.blockers = []
    mock_gate_report.coverage_summary = {}
    mock_gate_report.staging_summary = {}
    mock_gate.evaluate_scope.return_value = mock_gate_report

    app.dependency_overrides[require_admin] = lambda: {"role": "admin"}
    app.dependency_overrides[get_content_staging_seed_executor] = lambda: mock_seed_executor
    app.dependency_overrides[get_production_promotion_gate] = lambda: mock_gate
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_list = await client.get("/admin/content-factory/seed-runs")
        assert resp_list.status_code == 200
        assert resp_list.json()["total"] == 0

        fake_id = uuid.uuid4()
        resp_get = await client.get(f"/admin/content-factory/seed-runs/{fake_id}")
        assert resp_get.status_code == 404

        resp_gate = await client.get("/admin/content-factory/scopes/scope-1/production-gate")
        assert resp_gate.status_code == 200
        assert resp_gate.json()["status"] == "promotable"
