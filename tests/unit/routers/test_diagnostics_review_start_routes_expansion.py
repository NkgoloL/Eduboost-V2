import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.diagnostics import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_diagnostics_review_item_and_start_session():
    app = FastAPI()
    app.include_router(router)

    admin_ctx = MagicMock()
    admin_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    admin_ctx.roles = ["admin"]
    admin_ctx.is_admin = True

    mock_db = AsyncMock()
    app.dependency_overrides[require_auth_context] = lambda: admin_ctx
    app.dependency_overrides[get_db] = lambda: mock_db

    item_id = uuid.uuid4()
    mock_reviewed_item = MagicMock()
    mock_reviewed_item.item_id = item_id
    mock_reviewed_item.review_status = "approved"
    mock_reviewed_item.reviewer_id = uuid.UUID(admin_ctx.user_id)
    mock_reviewed_item.reviewed_at = None

    learner_id = uuid.uuid4()
    mock_snap = MagicMock()
    mock_snap.session_id = uuid.uuid4()
    mock_snap.learner_id = learner_id
    mock_snap.caps_ref = "CAPS.MATH.G4.1"
    mock_snap.theta = 0.0

    with patch("app.api_v2_routers.diagnostics.diagnostic_repositories.item_bank") as mock_ib_repo, \
         patch("app.api_v2_routers.diagnostics.ItemBankService") as mock_ib_service_cls, \
         patch("app.api_v2_routers.diagnostics.DiagnosticSessionService") as mock_dss_cls, \
         patch("app.api_v2_routers.diagnostics.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.diagnostics.require_active_consent_for_current_user", new=AsyncMock()):

        ib_svc_inst = MagicMock()
        ib_svc_inst.mark_item_reviewed = AsyncMock(return_value=mock_reviewed_item)
        mock_ib_service_cls.return_value = ib_svc_inst

        dss_inst = MagicMock()
        dss_inst.start_session = AsyncMock(return_value=mock_snap)
        mock_dss_cls.return_value = dss_inst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Review item bank item
            resp_rev = await client.post(
                f"/diagnostics/item-bank/items/{item_id}/review",
                json={
                    "review_status": "approved",
                    "quality_score": 0.9,
                },
            )
            assert resp_rev.status_code == 200
            data_rev = resp_rev.json()
            payload_rev = data_rev.get("data") if "data" in data_rev else data_rev
            assert payload_rev["item_id"] == str(item_id)
            assert payload_rev["review_status"] == "approved"

            # 2. Start diagnostic session
            resp_start = await client.post(
                "/diagnostics/sessions",
                json={
                    "learner_id": str(learner_id),
                    "caps_ref": "CAPS.MATH.G4.1",
                    "theta": 0.0,
                },
            )
            assert resp_start.status_code == 201
