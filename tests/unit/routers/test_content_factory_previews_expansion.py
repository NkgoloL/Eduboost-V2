import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_factory import (
    router,
    get_staging_preview_service,
    get_learner_read_service,
    get_content_coverage_service,
)
from app.api_v2_deps.auth import require_admin, require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_content_factory_staging_preview_and_reports():
    app = FastAPI()
    app.include_router(router)

    mock_staging_preview = AsyncMock()
    mock_staging_preview.preview_scope.return_value = {"scope_id": "scope-1", "items": []}
    mock_staging_preview.preview_caps_ref.return_value = {"caps_ref": "4.M.1.1", "items": []}

    mock_learner_read = AsyncMock()
    mock_learner_read.get_scope_content_summary.return_value = {"scope_id": "scope-1", "counts": {}}
    mock_learner_read.get_diagnostic_items.return_value = []
    mock_learner_read.get_lessons.return_value = []

    auth_ctx = MagicMock()
    auth_ctx.user_id = "adm-1"

    app.dependency_overrides[require_admin] = lambda: auth_ctx
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_staging_preview_service] = lambda: mock_staging_preview
    app.dependency_overrides[get_learner_read_service] = lambda: mock_learner_read
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_prev = await client.get("/admin/content-factory/staging-preview/scopes/scope-1")
        assert resp_prev.status_code == 200
        data_prev = resp_prev.json()
        assert (data_prev.get("data") or data_prev).get("scope_id") == "scope-1"

        resp_prod = await client.get("/admin/content-factory/production-preview/scopes/scope-1")
        assert resp_prod.status_code == 200
        data_prod = resp_prod.json()
        assert (data_prod.get("data") or data_prod).get("scope_id") == "scope-1"
