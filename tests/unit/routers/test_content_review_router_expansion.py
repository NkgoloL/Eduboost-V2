"""Comprehensive endpoint unit tests for the Content Review Governance Router."""
from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_review import (
    router,
    ReviewActor,
    get_review_actor,
    get_governance_service,
)
from app.api_v2_deps.auth import require_auth_context, AuthContext, TokenType
from app.models import UserRole
from app.core.database import get_db


# ---------------------------------------------------------------------------
# ReviewActor & Permission Logic Tests
# ---------------------------------------------------------------------------

class TestReviewActor:
    def test_review_actor_permission_granted(self):
        actor = ReviewActor(
            user_id="user_123",
            permissions=frozenset(["review", "assign"]),
            competencies=("mathematics",),
        )
        actor.require("review")
        actor.require("assign")

    def test_review_actor_permission_denied(self):
        actor = ReviewActor(
            user_id="user_123",
            permissions=frozenset(["review"]),
            competencies=(),
        )
        with pytest.raises(HTTPException) as exc:
            actor.require("publish")
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_review_actor_teacher():
    auth = AuthContext(
        user_id=str(uuid.uuid4()),
        roles=[UserRole.TEACHER],
        token_type=TokenType.ACCESS,
        raw_claims={"role": "teacher"},
        jti=str(uuid.uuid4()),
    )
    actor = await get_review_actor(auth)
    assert "review" in actor.permissions
    assert "assignment_accept" in actor.permissions


@pytest.mark.asyncio
async def test_get_review_actor_curriculum_lead():
    auth = AuthContext(
        user_id=str(uuid.uuid4()),
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={"role": "admin", "content_review_role": "curriculum_lead"},
        jti=str(uuid.uuid4()),
    )
    actor = await get_review_actor(auth)
    assert "publish" in actor.permissions
    assert "answer_key_verify" in actor.permissions
    assert "assign" in actor.permissions


@pytest.mark.asyncio
async def test_get_review_actor_no_permissions():
    auth = AuthContext(
        user_id=str(uuid.uuid4()),
        roles=[UserRole.STUDENT],
        token_type=TokenType.ACCESS,
        raw_claims={"role": "student"},
        jti=str(uuid.uuid4()),
    )
    with pytest.raises(HTTPException) as exc:
        await get_review_actor(auth)
    assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# Content Review Router Endpoints Tests
# ---------------------------------------------------------------------------

def _create_review_app(gov_service: Any | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    async def override_actor():
        return ReviewActor(
            user_id=str(uuid.uuid4()),
            permissions=frozenset(["assign", "review", "quarantine", "revise", "publish", "history_read", "stale_read", "assignment_accept"]),
            competencies=("mathematics",),
        )

    async def override_db():
        return AsyncMock()

    app.dependency_overrides[get_review_actor] = override_actor
    app.dependency_overrides[get_db] = override_db
    if gov_service is not None:
        app.dependency_overrides[get_governance_service] = lambda: gov_service
    return app


@pytest.mark.asyncio
async def test_content_review_assign_reviewers_not_found():
    mock_service = AsyncMock()
    mock_service.assign_reviewers.side_effect = LookupError("Artifact not found")
    app = _create_review_app(gov_service=mock_service)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/content-review/artifacts/{fake_id}/assignments",
            json={
                "reviewer_ids": ["rev_1", "rev_2"],
                "reviewer_competencies": {"rev_1": ["mathematics"], "rev_2": ["mathematics"]},
            },
        )
        assert resp.status_code == 409


@pytest.mark.asyncio
async def test_content_review_accept_assignment_not_found():
    mock_service = AsyncMock()
    mock_service.accept_assignment.side_effect = LookupError("Assignment not found")
    app = _create_review_app(gov_service=mock_service)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/content-review/assignments/{fake_id}/accept",
            json={"conflict_of_interest": False},
        )
        assert resp.status_code == 404
