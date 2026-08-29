import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.learners import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_learners_mastery_endpoints_success():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    learner_id = "00000000-0000-0000-0000-000000000002"
    mock_learner = MagicMock()
    mock_learner.id = learner_id
    mock_learner.guardian_id = auth_ctx.user_id

    mock_db = AsyncMock()
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api_v2_routers.learners.LearnerService") as mock_lrn_svc_cls, \
         patch("app.api_v2_routers.learners.require_learner_read_for_current_user"), \
         patch("app.api_v2_routers.learners.require_active_consent_for_current_user", new=AsyncMock()):

        lrn_svc = MagicMock()
        lrn_svc.get_learner_summary = AsyncMock(return_value=mock_learner)
        lrn_svc.get_mastery = AsyncMock(return_value={"learner_id": learner_id, "nodes": []})
        lrn_svc.get_subject_mastery_summary = AsyncMock(return_value={"Mathematics": 0.85})
        lrn_svc.get_topic_mastery = AsyncMock(return_value={"caps_ref": "CAPS.MATH.G4.1", "p_mastery": 0.9})
        mock_lrn_svc_cls.return_value = lrn_svc

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Get mastery
            resp_m = await client.get(f"/learners/{learner_id}/mastery")
            assert resp_m.status_code == 200
            data_m = resp_m.json()
            payload_m = data_m.get("data") if "data" in data_m else data_m
            assert payload_m["learner_id"] == learner_id

            # 2. Get mastery summary
            resp_sum = await client.get(f"/learners/{learner_id}/mastery/summary")
            assert resp_sum.status_code == 200
            data_sum = resp_sum.json()
            payload_sum = data_sum.get("data") if "data" in data_sum else data_sum
            assert payload_sum["Mathematics"] == 0.85

            # 3. Get topic mastery
            resp_top = await client.get(f"/learners/{learner_id}/mastery/CAPS.MATH.G4.1")
            assert resp_top.status_code == 200
            data_top = resp_top.json()
            payload_top = data_top.get("data") if "data" in data_top else data_top
            assert payload_top["caps_ref"] == "CAPS.MATH.G4.1"
