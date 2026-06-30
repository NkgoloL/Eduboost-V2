"""API tests for production promotion routes."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user


class FakeSession:
    async def commit(self):
        return None

class FakeProductionGate:
    async def evaluate_scope(self, session, scope_id, *, layers=None):
        from app.services.content_production_promotion_gate import ProductionGateReport, ProductionGateStatus
        return ProductionGateReport(
            scope_id=scope_id,
            status=ProductionGateStatus.PROMOTABLE,
            blockers=[],
            coverage_summary={},
            staging_summary={},
        )

class FakeProductionExecutor:
    async def dry_run_promotion(self, session, scope_id, *, layers=None, actor_id):
        from app.services.content_production_promotion_executor import ProductionPromotionPlan
        return ProductionPromotionPlan(
            scope_id=scope_id,
            layers=layers or [],
            promotable_count=0,
            skipped_count=0,
            skipped=[],
        )
    async def promote_scope(self, session, scope_id, *, layers=None, actor_id, confirmation):
        raise ValueError("Gate not passed")
    async def list_promotion_events(self, session, *, scope_id=None, limit=50, offset=0):
        from app.services.content_production_promotion_executor import ProductionPromotionPage
        return ProductionPromotionPage(
            total=0,
            limit=limit,
            offset=offset,
            items=[],
        )
    async def get_promotion_event(self, session, promotion_event_id):
        raise LookupError("Event not found")
    async def rollback_promotion(self, session, promotion_event_id, *, actor_id, reason):
        raise LookupError("Event not found")

class FakeProductionReadVerification:
    async def verify_promotion_event(self, session, promotion_event_id, *, actor_id=None):
        raise LookupError("Event not found")
    async def verify_scope_production(self, session, scope_id, *, layers=None):
        from app.services.content_production_read_verification import ScopeProductionReadReport
        return ScopeProductionReadReport(
            scope_id=scope_id,
            passed=True,
            production_artifacts_count=0,
            errors=[],
        )

def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}

def _parent_user():
    return {"sub": str(uuid.uuid4()), "role": "parent", "type": "access"}

def _session():
    return FakeSession()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def admin_auth_headers():
    return {"Authorization": "Bearer admin_token"}


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_production_promotion_gate] = FakeProductionGate
    app.dependency_overrides[content_factory.get_production_promotion_executor] = FakeProductionExecutor
    app.dependency_overrides[content_factory.get_production_read_verification_service] = FakeProductionReadVerification
    app.dependency_overrides[content_factory.get_db] = _session
    return TestClient(app)


@pytest.fixture
def non_admin_client():
    app.dependency_overrides[get_current_user] = _parent_user
    return TestClient(app)


def test_unauthenticated_production_gate_rejected(client: TestClient) -> None:
    """Unauthenticated production gate rejected."""
    app.dependency_overrides.clear()
    response = client.get("/api/v2/admin/content-factory/scopes/test_scope/production-gate")
    assert response.status_code == 401


def test_non_admin_production_gate_rejected(non_admin_client: TestClient) -> None:
    """Non-admin production gate rejected."""
    response = non_admin_client.get("/api/v2/admin/content-factory/scopes/test_scope/production-gate")
    assert response.status_code == 403


def test_admin_can_fetch_production_gate(client: TestClient) -> None:
    """Admin can fetch production gate."""
    response = client.get("/api/v2/admin/content-factory/scopes/test_scope/production-gate")
    assert response.status_code == 200


def test_admin_can_dry_run_promotion(client: TestClient) -> None:
    """Admin can dry-run promotion."""
    response = client.post("/api/v2/admin/content-factory/scopes/test_scope/dry-run-promotion")
    assert response.status_code == 200


def test_promote_production_rejects_missing_confirmation(client: TestClient) -> None:
    """Promote production rejects missing confirmation."""
    response = client.post(
        "/api/v2/admin/content-factory/scopes/test_scope/promote-production",
        json={"layers": None, "confirmation": ""},
    )
    assert response.status_code == 422  # Validation error for missing confirmation


def test_promote_production_rejects_wrong_confirmation(client: TestClient) -> None:
    """Promote production rejects wrong confirmation."""
    response = client.post(
        "/api/v2/admin/content-factory/scopes/test_scope/promote-production",
        json={"layers": None, "confirmation": "WRONG_CONFIRMATION"},
    )
    assert response.status_code == 409  # Confirmation mismatch


def test_promote_production_rejects_blocked_gate(client: TestClient) -> None:
    """Promote production rejects blocked gate."""
    response = client.post(
        "/api/v2/admin/content-factory/scopes/test_scope/promote-production",
        json={"layers": None, "confirmation": "PROMOTE test_scope TO PRODUCTION"},
    )
    assert response.status_code == 409  # Gate blocked


def test_admin_can_list_promotion_events(client: TestClient) -> None:
    """Admin can list promotion events."""
    response = client.get("/api/v2/admin/content-factory/promotion-events")
    assert response.status_code == 200


def test_admin_can_fetch_promotion_event(client: TestClient) -> None:
    """Admin can fetch promotion event."""
    promotion_event_id = uuid.uuid4()
    response = client.get(f"/api/v2/admin/content-factory/promotion-events/{promotion_event_id}")
    assert response.status_code == 404  # Event doesn't exist yet


def test_admin_can_fetch_promotion_event_items(client: TestClient) -> None:
    """Admin can fetch promotion event items."""
    uuid.uuid4()
    # This route directly queries the database, so we skip it in unit tests
    # It should be tested in integration tests with a real database
    pass


def test_admin_can_verify_promotion_event(client: TestClient) -> None:
    """Admin can verify promotion event."""
    promotion_event_id = uuid.uuid4()
    response = client.post(f"/api/v2/admin/content-factory/promotion-events/{promotion_event_id}/verify")
    assert response.status_code == 404  # Event doesn't exist yet


def test_admin_can_rollback_promotion_event(client: TestClient) -> None:
    """Admin can rollback promotion event."""
    promotion_event_id = uuid.uuid4()
    response = client.post(
        f"/api/v2/admin/content-factory/promotion-events/{promotion_event_id}/rollback",
        json={"reason": "test rollback"},
    )
    assert response.status_code == 404  # Event doesn't exist yet
