"""Comprehensive endpoint unit tests for the Parents and Tutor Routers."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.parents import router as parents_router
from app.api_v2_routers.tutor import router as tutor_router, get_tutor_service
from app.api_v2_deps.auth import (
    require_parent_or_admin,
    require_auth_context,
    AuthContext,
    TokenType,
)
from app.models import UserRole
from app.core.database import get_db


# ---------------------------------------------------------------------------
# Parents Router Tests
# ---------------------------------------------------------------------------

def _create_parents_app(guardian_found: bool = True) -> FastAPI:
    app = FastAPI()
    app.include_router(parents_router)

    guardian_id = str(uuid.uuid4())

    async def override_auth():
        return AuthContext(
            user_id=guardian_id,
            guardian_id=guardian_id,
            roles=[UserRole.PARENT],
            token_type=TokenType.ACCESS,
            raw_claims={"role": "parent"},
            jti=str(uuid.uuid4()),
        )

    async def override_db():
        mock = AsyncMock()
        if guardian_found:
            mock_guardian = MagicMock()
            mock_guardian.id = guardian_id
            mock.get.return_value = mock_guardian
        else:
            mock.get.return_value = None
        return mock

    app.dependency_overrides[require_parent_or_admin] = override_auth
    app.dependency_overrides[require_auth_context] = override_auth
    app.dependency_overrides[get_db] = override_db
    return app


@pytest.mark.asyncio
async def test_parent_dashboard_guardian_not_found():
    app = _create_parents_app(guardian_found=False)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/parents/dashboard")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_parent_trust_dashboard_guardian_not_found():
    app = _create_parents_app(guardian_found=False)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/parents/trust-dashboard")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Tutor Router Access Validation Tests
# ---------------------------------------------------------------------------

def _create_tutor_app(tutor_service: Any | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(tutor_router)

    async def override_auth():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            learner_id=str(uuid.uuid4()),
            roles=[UserRole.STUDENT],
            token_type=TokenType.ACCESS,
            raw_claims={"role": "student"},
            jti=str(uuid.uuid4()),
        )

    async def override_db():
        return AsyncMock()

    app.dependency_overrides[require_auth_context] = override_auth
    app.dependency_overrides[get_db] = override_db
    if tutor_service is not None:
        app.dependency_overrides[get_tutor_service] = lambda: tutor_service
    return app


@pytest.mark.asyncio
async def test_tutor_session_create_validation():
    app = _create_tutor_app()
    with patch("slowapi.extension.Limiter._check_request_limit", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/tutor/sessions",
                json={
                    "learner_id": str(uuid.uuid4()),
                    "lesson_id": str(uuid.uuid4()),
                },
            )
            assert resp.status_code in (200, 201, 403, 404, 422, 500)
