"""Comprehensive unit tests for Content Factory admin router endpoints."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.api_v2 import app
from app.api_v2_deps.auth import AuthContext, TokenType, require_admin
from app.domain.content_scope import ContentScope, ContentScopeStatus
from app.domain.content_coverage import ContentLayer
from app.services.content_production_promotion_gate import ProductionGateStatus, ProductionGateReport


@pytest.fixture
def admin_auth_override():
    admin_ctx = AuthContext(
        user_id="admin-user-id",
        roles=["admin"],
        token_type=TokenType.ACCESS,
        jti="jti-admin-1",
        tenant_id="tenant-1",
        raw_claims={},
    )
    app.dependency_overrides[require_admin] = lambda: admin_ctx
    yield admin_ctx
    app.dependency_overrides.pop(require_admin, None)


@pytest.mark.asyncio
async def test_get_scopes_endpoint(admin_auth_override):
    scope = ContentScope(
        scope_id="grade4_maths",
        grade=4,
        subject="Mathematics",
        subject_code="MATHS",
        language="en",
        curriculum="CAPS",
        status=ContentScopeStatus.ACTIVE,
        caps_refs=["4.M.1.1"],
    )
    with patch("app.api_v2_routers.content_factory.ContentScopeRegistry") as mock_registry_cls:
        mock_reg = MagicMock()
        mock_reg.list_scopes.return_value = [scope]
        mock_registry_cls.return_value = mock_reg

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/v2/admin/content-factory/scopes")
            assert res.status_code == 200
            data = res.json()
            assert "data" in data or "items" in data or isinstance(data, list)


@pytest.mark.asyncio
async def test_get_single_scope_endpoint(admin_auth_override):
    scope = ContentScope(
        scope_id="grade4_maths",
        grade=4,
        subject="Mathematics",
        subject_code="MATHS",
        language="en",
        curriculum="CAPS",
        status=ContentScopeStatus.ACTIVE,
        caps_refs=["4.M.1.1"],
    )
    with patch("app.api_v2_routers.content_factory.ContentScopeRegistry") as mock_registry_cls:
        mock_reg = MagicMock()
        mock_reg.get_scope.return_value = scope
        mock_registry_cls.return_value = mock_reg

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/v2/admin/content-factory/scopes/grade4_maths")
            assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_production_gate_endpoint(admin_auth_override):
    mock_gate_report = ProductionGateReport(
        scope_id="grade4_maths",
        status=ProductionGateStatus.PROMOTABLE,
        blockers=[],
        coverage_summary={},
        staging_summary={},
    )
    with patch("app.api_v2_routers.content_factory.ContentProductionPromotionGate") as mock_gate_cls:
        mock_gate = MagicMock()
        mock_gate.evaluate_scope = AsyncMock(return_value=mock_gate_report)
        mock_gate_cls.return_value = mock_gate

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/v2/admin/content-factory/scopes/grade4_maths/production-gate")
            assert res.status_code == 200
            data = res.json()
            content = data.get("data", data)
            assert content["status"] == "promotable"
