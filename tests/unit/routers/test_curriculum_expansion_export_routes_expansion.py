import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.curriculum_expansion import router
from app.api_v2_deps.auth import require_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_curriculum_expansion_export_error_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "admin-usr"
    auth_ctx.roles = ["admin"]

    session = AsyncMock()
    app.dependency_overrides[require_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    manifest_id = uuid.uuid4()

    with patch("app.api_v2_routers.curriculum_expansion.TrainingDatasetGovernanceService") as MockGovService:
        gov_mock = MagicMock()
        MockGovService.return_value = gov_mock

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Test LookupError -> 404
            gov_mock.export_manifest = AsyncMock(side_effect=LookupError("Manifest not found"))
            resp_404 = await client.post(
                f"/admin/curriculum-expansion/training-manifests/{manifest_id}/export",
                json={"output_name": "training-export-v1.jsonl"},
            )
            assert resp_404.status_code == 404
            assert "Manifest not found" in resp_404.json()["detail"]

            # 2. Test PermissionError -> 409
            gov_mock.export_manifest = AsyncMock(side_effect=PermissionError("Manifest not approved"))
            resp_409 = await client.post(
                f"/admin/curriculum-expansion/training-manifests/{manifest_id}/export",
                json={"output_name": "training-export-v1.jsonl"},
            )
            assert resp_409.status_code == 409
            assert "Manifest not approved" in resp_409.json()["detail"]

            # 3. Test RuntimeError -> 422
            gov_mock.export_manifest = AsyncMock(side_effect=RuntimeError("Export serialization failed"))
            resp_422 = await client.post(
                f"/admin/curriculum-expansion/training-manifests/{manifest_id}/export",
                json={"output_name": "training-export-v1.jsonl"},
            )
            assert resp_422.status_code == 422
            assert "Export serialization failed" in resp_422.json()["detail"]
