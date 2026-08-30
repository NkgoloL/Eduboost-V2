import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.curriculum_expansion import router
from app.api_v2_deps.auth import require_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_curriculum_expansion_manifest_decision_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "admin-reviewer"
    auth_ctx.roles = ["admin"]

    session = AsyncMock()

    app.dependency_overrides[require_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    manifest_id = uuid.uuid4()

    # 1. Test get manifest 404
    session.get = AsyncMock(return_value=None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_get_404 = await client.get(f"/admin/curriculum-expansion/training-manifests/{manifest_id}")
        assert resp_get_404.status_code == 404
        assert "Training dataset manifest not found" in resp_get_404.json()["detail"]

    # 2. Test decision lookup error 404
    with patch("app.api_v2_routers.curriculum_expansion.TrainingDatasetGovernanceService") as MockGovService:
        gov_mock = MagicMock()
        gov_mock.approve_manifest = AsyncMock(side_effect=LookupError("Manifest not found"))
        MockGovService.return_value = gov_mock

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_dec_404 = await client.post(
                f"/admin/curriculum-expansion/training-manifests/{manifest_id}/decision",
                json={"decision": "approve", "reason": "Verified quality rubric and CAPS alignment"},
            )
            assert resp_dec_404.status_code == 404
            assert "Manifest not found" in resp_dec_404.json()["detail"]
