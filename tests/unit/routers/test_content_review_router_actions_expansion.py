import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_review import (
    router,
    ReviewActor,
    get_review_actor,
    get_governance_service,
)
from app.core.database import get_db


@pytest.mark.asyncio
async def test_content_review_quarantine_and_publish_routes():
    app = FastAPI()
    app.include_router(router)

    actor = ReviewActor(
        user_id="actor-lead",
        permissions=frozenset({"quarantine", "revise", "publish", "history_read"}),
        competencies=("MATHS",),
    )
    mock_service = AsyncMock()
    mock_service.quarantine_artifact.side_effect = LookupError("Artifact not found for quarantine")
    mock_service.publish_artifact.side_effect = LookupError("Artifact not found for publish")

    app.dependency_overrides[get_review_actor] = lambda: actor
    app.dependency_overrides[get_governance_service] = lambda: mock_service
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_q = await client.post(
            f"/content-review/artifacts/{fake_id}/quarantine",
            json={"reason_code": "safety_violation", "reason": "Unsafe content detected"},
        )
        assert resp_q.status_code == 404

        resp_p = await client.post(
            f"/content-review/artifacts/{fake_id}/publish",
            json={"expected_version": 1, "reason": "Published after consensus"},
        )
        assert resp_p.status_code == 404
