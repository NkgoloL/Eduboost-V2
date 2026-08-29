import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.popia import router
from app.api_v2_deps.consent_lifecycle import get_canonical_data_rights_service
from app.api_v2_deps.auth import require_auth_context


@pytest.mark.asyncio
async def test_popia_correction_and_restriction_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    learner_id = uuid.uuid4()

    mock_dsr_svc = MagicMock()
    mock_dsr_svc.request_correction = AsyncMock(return_value={"request_id": "corr-1", "status": "pending"})
    mock_dsr_svc.restrict_processing = AsyncMock(return_value={"request_id": "rest-1", "status": "restricted"})

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_canonical_data_rights_service] = lambda: mock_dsr_svc

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Correction request
        resp_corr = await client.post(
            "/popia/correction",
            json={
                "learner_id": str(learner_id),
                "fields": {"display_name": "Alexander"},
                "reason": "name_typo",
            },
        )
        assert resp_corr.status_code == 200
        data_corr = resp_corr.json()
        payload_corr = data_corr.get("data") if "data" in data_corr else data_corr
        assert payload_corr["request_id"] == "corr-1"

        # 2. Restriction request
        resp_rest = await client.post(
            "/popia/restriction",
            json={
                "learner_id": str(learner_id),
                "reason": "pending_verification",
            },
        )
        assert resp_rest.status_code == 200
        data_rest = resp_rest.json()
        payload_rest = data_rest.get("data") if "data" in data_rest else data_rest
        assert payload_rest["request_id"] == "rest-1"
