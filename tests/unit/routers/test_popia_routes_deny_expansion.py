import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.popia import router
from app.api_v2_deps.consent_lifecycle import (
    get_canonical_consent_service,
)
from app.api_v2_deps.auth import require_auth_context
from app.domain.consent import ConsentRecord, ConsentState


@pytest.mark.asyncio
async def test_popia_deny_consent_endpoint():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    learner_id = uuid.uuid4()
    guardian_id = uuid.uuid4()

    mock_consent_svc = AsyncMock()
    mock_consent_svc.deny.return_value = ConsentRecord(
        id=uuid.uuid4(),
        learner_id=learner_id,
        guardian_id=guardian_id,
        state=ConsentState.DENIED,
        privacy_notice_version="1.0",
        granted_at=None,
        expires_at=None,
        denied_at=datetime.now(timezone.utc),
        withdrawn_at=None,
        denial_reason="guardian_denial",
    )

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_canonical_consent_service] = lambda: mock_consent_svc

    with patch("app.api_v2_routers.popia._enforce_popia_learner_write", new=AsyncMock()), \
         patch("app.api_v2_routers.popia._authenticated_actor_id", return_value="user-123"):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/popia/consent/deny",
                json={
                    "learner_id": str(learner_id),
                    "guardian_id": str(guardian_id),
                    "privacy_notice_version": "1.0",
                    "reason": "guardian_denial",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert (data.get("data") or data).get("state") == "denied"
            assert (data.get("data") or data).get("denial_reason") == "guardian_denial"
