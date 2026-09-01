"""Batch 217 — app/api_v2_routers/content_factory.py production promotion & verification routes coverage expansion.

Tests endpoints:
- GET /admin/content-factory/scopes/{scope_id}/production-gate
- POST /admin/content-factory/scopes/{scope_id}/dry-run-promotion (success, 409 on ValueError)
- POST /admin/content-factory/scopes/{scope_id}/promote-production (with request, fallback seed_service, 409 on ValueError)
- GET /admin/content-factory/promotion-events (list page)
- GET /admin/content-factory/promotion-events/{promotion_event_id} (success, 404 on LookupError)
- GET /admin/content-factory/promotion-events/{promotion_event_id}/items
- POST /admin/content-factory/promotion-events/{promotion_event_id}/rollback (success, 404 on LookupError)
- GET /admin/content-factory/scopes/{scope_id}/production-read-verification
- GET /admin/content-factory/reports/{scope_id}
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api_v2_deps.auth import AuthContext, require_admin, require_auth_context
from app.api_v2_routers.content_factory import (
    get_db,
    get_production_promotion_executor,
    get_production_promotion_gate,
    get_production_read_verification_service,
    get_seed_promotion_service,
    router,
)
from app.domain.content_coverage import ContentLayer
from app.services.content_production_promotion_executor import (
    ProductionPromotionPage,
    ProductionPromotionPlan,
    ProductionPromotionResult,
    ProductionRollbackResult,
)
from app.services.content_production_promotion_gate import (
    ProductionGateBlocker,
    ProductionGateReport,
    ProductionGateStatus,
)
from app.services.content_production_read_verification import (
    ProductionReadVerificationReport,
    ScopeProductionReadReport,
)


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    # Override auth dependencies
    mock_auth = AuthContext(
        user_id="admin-user-123",
        email="admin@eduboost.co.za",
        role="admin",
        scopes=["admin:all"],
        token_type="access",
        raw_claims={},
        jti="jti-123",
    )
    app.dependency_overrides[require_admin] = lambda: mock_auth
    app.dependency_overrides[require_auth_context] = lambda: mock_auth

    # Mock DB session
    mock_session = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /admin/content-factory/scopes/{scope_id}/production-gate
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_production_gate_success(app, client):
    mock_gate = MagicMock()
    report = ProductionGateReport(
        scope_id="scope-123",
        status=ProductionGateStatus.PROMOTABLE,
        blockers=[],
        coverage_summary={"lessons": {"status": "green"}},
        staging_summary={"seeded_count": 5},
    )
    mock_gate.evaluate_scope = AsyncMock(return_value=report)
    app.dependency_overrides[get_production_promotion_gate] = lambda: mock_gate

    response = client.get("/admin/content-factory/scopes/scope-123/production-gate")
    assert response.status_code == 200
    data = response.json()
    assert data["scope_id"] == "scope-123"
    assert data["status"] == "promotable"
    assert len(data["blockers"]) == 0


@pytest.mark.unit
def test_get_production_gate_with_blockers(app, client):
    mock_gate = MagicMock()
    report = ProductionGateReport(
        scope_id="scope-123",
        status=ProductionGateStatus.BLOCKED_BY_COVERAGE,
        blockers=[
            ProductionGateBlocker(type="coverage", message="Coverage is red"),
        ],
    )
    mock_gate.evaluate_scope = AsyncMock(return_value=report)
    app.dependency_overrides[get_production_promotion_gate] = lambda: mock_gate

    response = client.get("/admin/content-factory/scopes/scope-123/production-gate")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked_by_coverage"
    assert len(data["blockers"]) == 1
    assert data["blockers"][0]["type"] == "coverage"


# ---------------------------------------------------------------------------
# POST /admin/content-factory/scopes/{scope_id}/dry-run-promotion
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_dry_run_promotion_endpoint_success(app, client):
    mock_executor = MagicMock()
    plan = ProductionPromotionPlan(
        scope_id="scope-123",
        layers=["lessons"],
        promotable_count=3,
        skipped_count=0,
        skipped=[],
    )
    mock_executor.dry_run_promotion = AsyncMock(return_value=plan)
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_executor

    response = client.post("/admin/content-factory/scopes/scope-123/dry-run-promotion")
    assert response.status_code == 200
    data = response.json()
    assert data["scope_id"] == "scope-123"
    assert data["promotable_count"] == 3


@pytest.mark.unit
def test_dry_run_promotion_endpoint_conflict_error(app, client):
    mock_executor = MagicMock()
    mock_executor.dry_run_promotion = AsyncMock(side_effect=ValueError("Gate is blocked"))
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_executor

    response = client.post("/admin/content-factory/scopes/scope-123/dry-run-promotion")
    assert response.status_code == 409
    assert "Gate is blocked" in response.json()["detail"]


# ---------------------------------------------------------------------------
# POST /admin/content-factory/scopes/{scope_id}/promote-production
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_promote_production_endpoint_with_request(app, client):
    mock_executor = MagicMock()
    event_id = uuid.uuid4()
    result = ProductionPromotionResult(
        promotion_event_id=event_id,
        scope_id="scope-123",
        status="succeeded",
        promoted_count=5,
        skipped_count=0,
        errors=[],
    )
    mock_executor.promote_scope = AsyncMock(return_value=result)
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_executor

    payload = {
        "confirmation": "PROMOTE scope-123 TO PRODUCTION",
        "layers": ["lessons"],
    }
    response = client.post("/admin/content-factory/scopes/scope-123/promote-production", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "succeeded"
    assert data["promoted_count"] == 5


@pytest.mark.unit
def test_promote_production_endpoint_fallback_seed_service(app, client):
    mock_seed = MagicMock()
    event_id = uuid.uuid4()
    result = ProductionPromotionResult(
        promotion_event_id=event_id,
        scope_id="scope-123",
        status="succeeded",
        promoted_count=2,
        skipped_count=0,
        errors=[],
    )
    mock_seed.promote_production = AsyncMock(return_value=result)
    app.dependency_overrides[get_seed_promotion_service] = lambda: mock_seed

    # Sending without request body triggers fallback
    response = client.post("/admin/content-factory/scopes/scope-123/promote-production")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "succeeded"
    assert data["promoted_count"] == 2


@pytest.mark.unit
def test_promote_production_endpoint_conflict_error(app, client):
    mock_executor = MagicMock()
    mock_executor.promote_scope = AsyncMock(side_effect=ValueError("Confirmation mismatch"))
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_executor

    payload = {
        "confirmation": "WRONG",
    }
    response = client.post("/admin/content-factory/scopes/scope-123/promote-production", json=payload)
    assert response.status_code == 409
    assert "Confirmation mismatch" in response.json()["detail"]


# ---------------------------------------------------------------------------
# GET /admin/content-factory/promotion-events
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_list_promotion_events_endpoint(app, client):
    mock_executor = MagicMock()
    event_id = uuid.uuid4()
    item = ProductionPromotionResult(
        promotion_event_id=event_id,
        scope_id="scope-123",
        status="succeeded",
        promoted_count=3,
        skipped_count=0,
        errors=[],
    )
    page = ProductionPromotionPage(
        total=1,
        limit=50,
        offset=0,
        items=[item],
    )
    mock_executor.list_promotion_events = AsyncMock(return_value=page)
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_executor

    response = client.get("/admin/content-factory/promotion-events")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["scope_id"] == "scope-123"


# ---------------------------------------------------------------------------
# GET /admin/content-factory/promotion-events/{promotion_event_id}
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_promotion_event_endpoint_success(app, client):
    mock_executor = MagicMock()
    event_id = uuid.uuid4()
    item = ProductionPromotionResult(
        promotion_event_id=event_id,
        scope_id="scope-123",
        status="succeeded",
        promoted_count=4,
        skipped_count=0,
        errors=[],
    )
    mock_executor.get_promotion_event = AsyncMock(return_value=item)
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_executor

    response = client.get(f"/admin/content-factory/promotion-events/{event_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["promotion_event_id"] == str(event_id)
    assert data["promoted_count"] == 4


@pytest.mark.unit
def test_get_promotion_event_endpoint_not_found(app, client):
    mock_executor = MagicMock()
    mock_executor.get_promotion_event = AsyncMock(side_effect=LookupError("Event not found"))
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_executor

    event_id = uuid.uuid4()
    response = client.get(f"/admin/content-factory/promotion-events/{event_id}")
    assert response.status_code == 404
    assert "Event not found" in response.json()["detail"]


# ---------------------------------------------------------------------------
# GET /admin/content-factory/promotion-events/{promotion_event_id}/items
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_promotion_event_items_endpoint(app, client):
    mock_session = AsyncMock()
    art_id = uuid.uuid4()
    item = MagicMock(
        id=uuid.uuid4(),
        artifact_id=art_id,
        staging_artifact_id=uuid.uuid4(),
        scope_id="scope-123",
        caps_ref="MATH.4.1",
        layer="lessons",
        artifact_type="lesson_plan",
        production_status="active",
    )
    res = MagicMock()
    res.scalars.return_value.all.return_value = [item]
    mock_session.execute.return_value = res
    app.dependency_overrides[get_db] = lambda: mock_session

    event_id = uuid.uuid4()
    response = client.get(f"/admin/content-factory/promotion-events/{event_id}/items")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["artifact_id"] == str(art_id)
    assert data["items"][0]["production_status"] == "active"


# ---------------------------------------------------------------------------
# POST /admin/content-factory/promotion-events/{promotion_event_id}/rollback
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_rollback_promotion_endpoint_success(app, client):
    mock_executor = MagicMock()
    event_id = uuid.uuid4()
    result = ProductionRollbackResult(
        promotion_event_id=event_id,
        status="rolled_back",
        rolled_back_count=3,
    )
    mock_executor.rollback_promotion = AsyncMock(return_value=result)
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_executor

    payload = {"reason": "Quality check failure"}
    response = client.post(f"/admin/content-factory/promotion-events/{event_id}/rollback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rolled_back"
    assert data["rolled_back_count"] == 3


# ---------------------------------------------------------------------------
# GET /admin/content-factory/scopes/{scope_id}/production-read-verification
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_production_read_verification_endpoint(app, client):
    mock_verify = MagicMock()
    report = ScopeProductionReadReport(
        scope_id="scope-123",
        passed=True,
        production_artifacts_count=10,
        errors=[],
    )
    mock_verify.verify_scope_production = AsyncMock(return_value=report)
    app.dependency_overrides[get_production_read_verification_service] = lambda: mock_verify

    response = client.get("/admin/content-factory/scopes/scope-123/production-read-verification")
    assert response.status_code == 200
    data = response.json()
    assert data["passed"] is True
    assert data["production_artifacts_count"] == 10
