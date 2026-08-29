import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_factory import (
    router,
    _value,
    _mcp_runtime_imported,
    _generation_enabled,
)
from app.api_v2_deps.auth import require_admin
from app.core.database import get_db
from app.models.content_factory import ContentArtifactStatus


def test_internal_helpers():
    assert _value(ContentArtifactStatus.PUBLISHED) == "published"
    assert _value("simple_str") == "simple_str"
    assert isinstance(_mcp_runtime_imported(), bool)
    assert isinstance(_generation_enabled(), bool)


@pytest.mark.asyncio
async def test_content_factory_full_generation_runs_list():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "adm-1"

    session = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = []
    session.execute.return_value = mock_res

    app.dependency_overrides[require_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/full-generation/runs")
        assert resp.status_code == 200
        data = resp.json()
        assert (data.get("data") or data).get("total") == 0
