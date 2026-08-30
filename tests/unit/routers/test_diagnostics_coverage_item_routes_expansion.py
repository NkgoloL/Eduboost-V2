import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.diagnostics import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_diagnostics_coverage_and_item_bank_item():
    app = FastAPI()
    app.include_router(router)

    admin_ctx = MagicMock()
    admin_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    admin_ctx.roles = ["admin"]
    admin_ctx.is_admin = True

    session = AsyncMock()
    app.dependency_overrides[require_auth_context] = lambda: admin_ctx
    app.dependency_overrides[get_db] = lambda: session

    item_id = uuid.uuid4()
    mock_item = MagicMock()
    mock_item.item_id = item_id
    mock_item.caps_ref = "CAPS.MATH.G4.1"
    mock_item.grade = 4
    mock_item.subject = "Mathematics"
    mock_item.term = 1
    mock_item.topic = "Numbers"
    mock_item.subtopic = "Addition"
    mock_item.skill = "Addition with regrouping"
    mock_item.stem = "What is 15 + 27?"
    mock_item.answer_key = "42"
    mock_item.options = ["32", "42", "52", "41"]
    mock_item.explanation = "15 + 27 = 42"
    mock_item.distractor_rationale = {}
    mock_item.misconception_tags = []
    mock_item.difficulty_b = 0.5
    mock_item.discrimination_a = 1.2
    mock_item.guessing_c = 0.25
    mock_item.review_status = "approved"
    mock_item.reviewer_id = None
    mock_item.reviewed_at = None
    mock_item.exposure_count = 0
    mock_item.max_exposure = 100
    mock_item.quality_score = 0.95
    mock_item.safety_passed = True

    with patch("app.api_v2_routers.diagnostics.diagnostic_repositories.item_bank") as mock_ib_repo, \
         patch("app.api_v2_routers.diagnostics.ItemBankService") as mock_ib_service:

        ib_repo_inst = MagicMock()
        ib_repo_inst.get_item = AsyncMock(return_value=mock_item)
        mock_ib_repo.return_value = ib_repo_inst

        ib_svc_inst = MagicMock()
        ib_svc_inst.get_coverage_summary = AsyncMock(
            return_value={"CAPS.MATH.G4.1": {"coverage_ratio": 1.0, "total_items": 10}}
        )
        mock_ib_service.return_value = ib_svc_inst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Test coverage summary
            resp_cov = await client.get("/diagnostics/coverage")
            assert resp_cov.status_code == 200

            # 2. Test get item bank item
            resp_item = await client.get(f"/diagnostics/item-bank/items/{item_id}")
            assert resp_item.status_code == 200
            data_item = resp_item.json()
            payload = data_item.get("data") if "data" in data_item else data_item
            assert payload["item_id"] == str(item_id)
            assert payload["grade"] == 4
