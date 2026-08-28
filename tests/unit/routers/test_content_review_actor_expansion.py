"""Comprehensive unit tests for content review actor resolution and permission enforcement."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext, TokenType
from app.api_v2_routers.content_review import (
    ReviewActor,
    get_review_actor,
)


class TestReviewActorPermissions:
    def test_require_permission_granted(self):
        actor = ReviewActor(
            user_id="user_123",
            permissions=frozenset({"review", "publish"}),
            competencies=("mathematics",),
        )
        actor.require("review")
        actor.require("publish")

    def test_require_permission_denied(self):
        actor = ReviewActor(
            user_id="user_123",
            permissions=frozenset({"review"}),
            competencies=(),
        )
        with pytest.raises(HTTPException) as exc_info:
            actor.require("publish")
        assert exc_info.value.status_code == 403


class TestGetReviewActor:
    @pytest.mark.asyncio
    async def test_get_review_actor_teacher(self):
        ctx = AuthContext(
            user_id="teacher_1",
            roles=["teacher"],
            token_type=TokenType.ACCESS,
            jti="jti-t1",
            tenant_id="tenant_1",
            raw_claims={"review_permissions": ["review"]},
        )
        actor = await get_review_actor(ctx)
        assert "review" in actor.permissions
        assert "history_read" in actor.permissions
        assert "assignment_accept" in actor.permissions

    @pytest.mark.asyncio
    async def test_get_review_actor_admin(self):
        ctx = AuthContext(
            user_id="admin_1",
            roles=["admin"],
            token_type=TokenType.ACCESS,
            jti="jti-a1",
            tenant_id="tenant_1",
            raw_claims={},
        )
        actor = await get_review_actor(ctx)
        assert "assign" in actor.permissions
        assert "quarantine" in actor.permissions
        assert "revise" in actor.permissions

    @pytest.mark.asyncio
    async def test_get_review_actor_curriculum_lead(self):
        ctx = AuthContext(
            user_id="lead_1",
            roles=[],
            token_type=TokenType.ACCESS,
            jti="jti-l1",
            tenant_id="tenant_1",
            raw_claims={"content_review_role": "curriculum_lead"},
        )
        actor = await get_review_actor(ctx)
        assert "publish" in actor.permissions
        assert "answer_key_verify" in actor.permissions

    @pytest.mark.asyncio
    async def test_get_review_actor_no_permissions_raises(self):
        ctx = AuthContext(
            user_id="anonymous_1",
            roles=[],
            token_type=TokenType.ACCESS,
            jti="jti-anon",
            tenant_id="tenant_1",
            raw_claims={},
        )
        with pytest.raises(HTTPException) as exc_info:
            await get_review_actor(ctx)
        assert exc_info.value.status_code == 403
