import datetime
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.popia import router
from app.api_v2_deps.consent_lifecycle import get_canonical_consent_service
from app.api_v2_deps.auth import require_auth_context
from app.domain.consent import ConsentRecord, ConsentState


@pytest.mark.asyncio
async def test_popia_grant_and_withdraw_consent_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    learner_id = uuid.uuid4()
    guardian_id = uuid.uuid4()
    record_id = uuid.uuid4()

    mock_record_grant = ConsentRecord(
        id=record_id,
        learner_id=learner_id,
        guardian_id=guardian_id,
        state=ConsentState.GRANTED,
        privacy_notice_version="1.0",
        granted_at=datetime.datetime.now(datetime.timezone.utc),
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365),
    )

    mock_record_withdraw = ConsentRecord(
        id=record_id,
        learner_id=learner_id,
        guardian_id=guardian_id,
        state=ConsentState.WITHDRAWN,
        privacy_notice_version="1.0",
        granted_at=mock_record_grant.granted_at,
        withdrawn_at=datetime.datetime.now(datetime.timezone.utc),
    )

    mock_consent_svc = MagicMock()
    mock_consent_svc.grant = AsyncMock(return_value=mock_record_grant)
    mock_consent_svc.withdraw = AsyncMock(return_value=mock_record_withdraw)

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_canonical_consent_service] = lambda: mock_consent_svc

    with patch("app.api_v2_routers.popia._enforce_popia_learner_write", new=AsyncMock()), \
         patch("app.api_v2_routers.popia._authenticated_actor_id", return_value=str(guardian_id)):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Grant consent
            resp_grant = await client.post(
                "/popia/consent/grant",
                json={
                    "learner_id": str(learner_id),
                    "guardian_id": str(guardian_id),
                    "privacy_notice_version": "1.0",
                },
            )
            assert resp_grant.status_code == 200
            data_g = resp_grant.json()
            payload_g = data_g.get("data") if "data" in data_g else data_g
            assert payload_g["state"] == "granted"

            # 2. Withdraw consent
            resp_with = await client.post(
                "/popia/consent/withdraw",
                json={
                    "learner_id": str(learner_id),
                },
            )
            assert resp_with.status_code == 200
            data_w = resp_with.json()
            payload_w = data_w.get("data") if "data" in data_w else data_w
            assert payload_w["state"] == "withdrawn"
