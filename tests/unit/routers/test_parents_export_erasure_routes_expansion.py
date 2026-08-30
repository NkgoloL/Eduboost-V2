import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.parents import router
from app.api_v2_deps.auth import require_parent_or_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_parents_export_bundle_and_erasure_routes():
    app = FastAPI()
    app.include_router(router)

    guardian_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx = MagicMock()
    auth_ctx.user_id = guardian_id
    auth_ctx.roles = ["parent"]
    auth_ctx.is_admin = False

    learner_id = "00000000-0000-0000-0000-000000000002"
    mock_learner = MagicMock()
    mock_learner.id = learner_id
    mock_learner.display_name = "Alex"
    mock_learner.guardian_id = guardian_id

    mock_guardian = MagicMock()
    mock_guardian.id = guardian_id
    mock_guardian.subscription_tier = "premium"

    mock_db = AsyncMock()
    mock_db.get = AsyncMock(return_value=mock_guardian)

    app.dependency_overrides[require_parent_or_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api_v2_routers.parents.LearnerService") as mock_lrn_svc_cls, \
         patch("app.api_v2_routers.parents.POPIADataRightsService") as mock_popia_cls, \
         patch("app.api_v2_routers.parents.require_learner_read_for_current_user"), \
         patch("app.api_v2_routers.parents.require_active_consent_for_current_user", new=AsyncMock()):

        lrn_svc = MagicMock()
        lrn_svc.list_by_guardian = AsyncMock(return_value=[mock_learner])
        mock_lrn_svc_cls.return_value = lrn_svc

        popia_svc = MagicMock()
        popia_svc.request_erasure = AsyncMock(return_value={"request_id": "req-1", "status": "requested"})
        mock_popia_cls.return_value = popia_svc

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Export parent access bundle
            resp_exp = await client.get(f"/parents/{guardian_id}/export")
            assert resp_exp.status_code == 200
            data_exp = resp_exp.json()
            payload_exp = data_exp.get("data") if "data" in data_exp else data_exp
            assert payload_exp["guardian_id"] == guardian_id
            assert len(payload_exp["exports"]) == 1
            assert payload_exp["exports"][0]["learner_id"] == learner_id

            # 2. Request erasure
            resp_era = await client.delete(f"/parents/learners/{learner_id}")
            assert resp_era.status_code == 202
            data_era = resp_era.json()
            payload_era = data_era.get("data") if "data" in data_era else data_era
            assert payload_era["request_id"] == "req-1"
