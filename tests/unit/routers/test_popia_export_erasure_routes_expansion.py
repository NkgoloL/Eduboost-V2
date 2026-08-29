import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.popia import router
from app.api_v2_deps.consent_lifecycle import get_canonical_data_rights_service
from app.api_v2_deps.auth import require_auth_context


@pytest.mark.asyncio
async def test_popia_export_and_erasure_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    learner_id = uuid.uuid4()

    mock_dsr_svc = MagicMock()
    mock_dsr_svc.build_learner_export = AsyncMock(
        return_value={
            "filename": "export.json",
            "content_type": "application/json",
            "data": {"learner_id": str(learner_id)},
            "status": {"request_type": "export", "status": "completed"},
        }
    )
    mock_dsr_svc.request_erasure = AsyncMock(return_value={"request_id": "req-1", "status": "pending"})
    mock_dsr_svc.cancel_erasure = AsyncMock(return_value={"status": "cancelled"})
    mock_dsr_svc.erasure_status = AsyncMock(return_value={"status": "completed"})

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_canonical_data_rights_service] = lambda: mock_dsr_svc

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Export request
        resp_exp = await client.post(
            "/popia/exports",
            json={"learner_id": str(learner_id), "format": "json"},
        )
        assert resp_exp.status_code == 200
        data_exp = resp_exp.json()
        assert "data" in data_exp

        # 2. Erasure request
        resp_era = await client.post(
            "/popia/erasure",
            json={"learner_id": str(learner_id), "reason": "parent_request"},
        )
        assert resp_era.status_code == 201
        data_era = resp_era.json()
        payload_era = data_era.get("data") if "data" in data_era else data_era
        assert payload_era["request_id"] == "req-1"

        # 3. Erasure status
        resp_stat = await client.get(f"/popia/erasure/{learner_id}/status")
        assert resp_stat.status_code == 200
        data_stat = resp_stat.json()
        payload_stat = data_stat.get("data") if "data" in data_stat else data_stat
        assert payload_stat["status"] == "completed"

        # 4. Erasure cancel
        resp_can = await client.post(f"/popia/erasure/{learner_id}/cancel")
        assert resp_can.status_code == 200
        data_can = resp_can.json()
        payload_can = data_can.get("data") if "data" in data_can else data_can
        assert payload_can["status"] == "cancelled"
