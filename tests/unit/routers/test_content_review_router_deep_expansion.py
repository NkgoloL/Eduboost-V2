import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_review import (
    router,
    ReviewActor,
    get_review_actor,
    get_governance_service,
)
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.database import get_db


def test_review_actor_permissions():
    actor = ReviewActor(
        user_id="user1",
        permissions=frozenset({"review", "history_read"}),
        competencies=("MATHS",),
    )
    actor.require("review")
    actor.require("history_read")

    with pytest.raises(HTTPException) as exc_info:
        actor.require("assign")
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_review_actor_roles():
    auth_ctx_teacher = AuthContext(
        user_id=str(uuid.uuid4()),
        role="teacher",
        roles=["teacher"],
        email="teacher@school.za",
        token_type="access",
        raw_claims={"role": "teacher"},
        jti=str(uuid.uuid4()),
    )
    actor_teacher = await get_review_actor(auth_ctx_teacher)
    assert "review" in actor_teacher.permissions
    assert "assignment_accept" in actor_teacher.permissions

    auth_ctx_admin = AuthContext(
        user_id=str(uuid.uuid4()),
        role="admin",
        roles=["admin"],
        email="admin@eduboost.za",
        token_type="access",
        raw_claims={"role": "admin"},
        jti=str(uuid.uuid4()),
    )
    actor_admin = await get_review_actor(auth_ctx_admin)
    assert "assign" in actor_admin.permissions
    assert "quarantine" in actor_admin.permissions


@pytest.mark.asyncio
async def test_content_review_endpoints():
    app = FastAPI()
    app.include_router(router)

    actor = ReviewActor(
        user_id="actor-1",
        permissions=frozenset({"assign", "review", "assignment_accept", "quarantine"}),
        competencies=("MATHS",),
    )
    mock_service = AsyncMock()
    mock_service.assign_reviewers.side_effect = LookupError("Artifact not found")

    app.dependency_overrides[get_review_actor] = lambda: actor
    app.dependency_overrides[get_governance_service] = lambda: mock_service
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/content-review/artifacts/{fake_id}/assignments",
            json={
                "reviewer_ids": ["rev1", "rev2", "rev3"],
                "reviewer_competencies": {},
            },
        )
        assert resp.status_code == 409
