import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.study_plans import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_generate_study_plan_endpoint():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.study_plans.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.study_plans.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.study_plans.build_runtime_kg_study_plan_payload", new=AsyncMock(return_value={"kg": True})), \
         patch("app.api_v2_routers.study_plans.enqueue_durable", new=AsyncMock(return_value="job-123")):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/study-plans/generate/lrn-1", json={"gap_ratio": 0.5})
            assert resp.status_code == 202
            data = resp.json()
            assert (data.get("data") or data).get("job_id") == "job-123"
            assert (data.get("data") or data).get("operation") == "study_plan_generation"
