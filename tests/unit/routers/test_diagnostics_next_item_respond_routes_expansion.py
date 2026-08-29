import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.diagnostics import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_diagnostics_next_item_and_respond_success():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    session_id = uuid.uuid4()
    learner_id = "00000000-0000-0000-0000-000000000002"
    item_id = uuid.uuid4()

    mock_db = AsyncMock()
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_learner = MagicMock()
    mock_learner.id = learner_id
    mock_learner.guardian_id = auth_ctx.user_id

    mock_snap = MagicMock()
    mock_snap.learner_id = learner_id
    mock_snap.caps_ref = "CAPS.MATH.G4.1"

    mock_item = MagicMock()
    mock_item.item_id = item_id
    mock_item.caps_ref = "CAPS.MATH.G4.1"
    mock_item.stem = "What is 2 + 2?"
    mock_item.options = ["3", "4", "5"]

    mock_result = MagicMock()
    mock_result.theta = 0.5
    mock_result.standard_error = 0.2
    mock_result.completed = False

    with patch("app.api_v2_routers.diagnostics.diagnostic_repositories.learner") as mock_lrn_repo, \
         patch("app.api_v2_routers.diagnostics.diagnostic_repositories.item_bank") as mock_ib_repo, \
         patch("app.api_v2_routers.diagnostics.DiagnosticSessionService") as mock_dss_cls, \
         patch("app.api_v2_routers.diagnostics.require_learner_read_for_current_user"), \
         patch("app.api_v2_routers.diagnostics.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.diagnostics.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.diagnostics.validate_adaptive_diagnostic_response"):

        lrn_repo_inst = MagicMock()
        lrn_repo_inst.get_by_id = AsyncMock(return_value=mock_learner)
        mock_lrn_repo.return_value = lrn_repo_inst

        ib_repo_inst = MagicMock()
        ib_repo_inst.list_by_caps_ref = AsyncMock(return_value=[mock_item])
        ib_repo_inst.get_item = AsyncMock(return_value=mock_item)
        mock_ib_repo.return_value = ib_repo_inst

        dss_inst = MagicMock()
        dss_inst.recover_session = AsyncMock(return_value=mock_snap)
        dss_inst.get_next_item = AsyncMock(return_value=mock_item)
        dss_inst.submit_response = AsyncMock(return_value=mock_result)
        mock_dss_cls.return_value = dss_inst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Next item
            resp_next = await client.get(f"/diagnostics/sessions/{session_id}/next-item?caps_ref=CAPS.MATH.G4.1")
            assert resp_next.status_code == 200
            data_next = resp_next.json()
            payload_next = data_next.get("data") if "data" in data_next else data_next
            assert payload_next["completed"] is False
            assert payload_next["item_id"] == str(item_id)

            # 2. Respond
            resp_resp = await client.post(
                f"/diagnostics/sessions/{session_id}/respond",
                json={
                    "item_id": str(item_id),
                    "correct": True,
                    "response": "4",
                    "caps_ref": "CAPS.MATH.G4.1",
                },
            )
            assert resp_resp.status_code == 200
