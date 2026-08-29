import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.learners import router
from app.api_v2_deps.auth import require_parent_or_admin, require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_learners_create_and_get_success():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    learner_id = "00000000-0000-0000-0000-000000000002"
    mock_learner_data = {
        "id": learner_id,
        "guardian_id": auth_ctx.user_id,
        "pseudonym_id": "pseudo-123",
        "display_name": "Alex",
        "grade": 4,
        "language": "en",
        "archetype": "visual",
        "theta": 0.0,
        "xp": 100,
        "streak_days": 3,
        "created_at": "2026-08-29T10:00:00Z",
    }

    mock_db = AsyncMock()
    app.dependency_overrides[require_parent_or_admin] = lambda: auth_ctx
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api_v2_routers.learners.LearnerService") as mock_lrn_svc_cls, \
         patch("app.api_v2_routers.learners.require_learner_read_for_current_user"), \
         patch("app.api_v2_routers.learners.require_active_consent_for_current_user", new=AsyncMock()):

        lrn_svc = MagicMock()
        lrn_svc.create_learner = AsyncMock(return_value=mock_learner_data)
        lrn_svc.get_learner_summary = AsyncMock(return_value=mock_learner_data)
        mock_lrn_svc_cls.return_value = lrn_svc

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Create learner
            resp_create = await client.post(
                "/learners/",
                json={
                    "display_name": "Alex",
                    "grade": 4,
                    "language": "en",
                },
            )
            assert resp_create.status_code == 201
            data_c = resp_create.json()
            payload_c = data_c.get("data") if "data" in data_c else data_c
            assert payload_c["id"] == learner_id
            assert payload_c["display_name"] == "Alex"

            # 2. Get learner
            resp_get = await client.get(f"/learners/{learner_id}")
            assert resp_get.status_code == 200
            data_g = resp_get.json()
            payload_g = data_g.get("data") if "data" in data_g else data_g
            assert payload_g["id"] == learner_id
