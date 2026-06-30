"""API tests for learner content routes."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import learner_content
from app.core.security import get_current_user


class FakeSession:
    async def commit(self):
        return None


class FakeLearnerReadService:
    async def get_diagnostic_items(self, session, *, scope_id, caps_ref=None, limit=20):
        return []

    async def get_lessons(self, session, *, scope_id, caps_ref=None, limit=20):
        return []

    async def get_scope_content_summary(self, session, scope_id):
        from app.services.content_learner_read_service import LearnerScopeContentSummary
        return LearnerScopeContentSummary(
            scope_id=scope_id,
            diagnostic_items_count=0,
            lessons_count=0,
            total_artifacts_count=0,
            last_promotion_at=None,
        )


def _learner_user():
    return {"sub": str(uuid.uuid4()), "role": "learner", "type": "access"}


def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


def _session():
    return FakeSession()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = _learner_user
    app.dependency_overrides[learner_content.get_learner_read_service] = FakeLearnerReadService
    app.dependency_overrides[learner_content.get_db] = _session
    return TestClient(app)


@pytest.fixture
def admin_client():
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[learner_content.get_learner_read_service] = FakeLearnerReadService
    app.dependency_overrides[learner_content.get_db] = _session
    return TestClient(app)


def test_unauthenticated_learner_route_rejected(client: TestClient) -> None:
    """Unauthenticated learner route rejected."""
    app.dependency_overrides.clear()
    response = client.get("/api/v2/learner/content/scopes/test_scope/summary")
    assert response.status_code == 401


def test_learner_can_fetch_scope_summary(client: TestClient) -> None:
    """Learner can fetch scope summary."""
    response = client.get("/api/v2/learner/content/scopes/test_scope/summary")
    assert response.status_code == 200


def test_learner_can_fetch_diagnostic_items(client: TestClient) -> None:
    """Learner can fetch diagnostic items."""
    response = client.get("/api/v2/learner/content/scopes/test_scope/diagnostic-items")
    assert response.status_code == 200


def test_learner_can_fetch_lessons(client: TestClient) -> None:
    """Learner can fetch lessons."""
    response = client.get("/api/v2/learner/content/scopes/test_scope/lessons")
    assert response.status_code == 200


def test_learner_can_fetch_diagnostic_items_by_caps_ref(client: TestClient) -> None:
    """Learner can fetch diagnostic items by CAPS ref."""
    response = client.get("/api/v2/learner/content/scopes/test_scope/caps/test_ref/diagnostic-items")
    assert response.status_code == 200


def test_learner_can_fetch_lessons_by_caps_ref(client: TestClient) -> None:
    """Learner can fetch lessons by CAPS ref."""
    response = client.get("/api/v2/learner/content/scopes/test_scope/caps/test_ref/lessons")
    assert response.status_code == 200


def test_learner_route_is_not_under_admin(client: TestClient) -> None:
    """Learner route is not under /admin."""
    response = client.get("/api/v2/learner/content/scopes/test_scope/summary")
    assert response.status_code == 200
    # The route path should not contain /admin
    assert "/admin/" not in str(response.request.url)


def test_admin_can_also_access_learner_routes(admin_client: TestClient) -> None:
    """Admin can also access learner routes."""
    response = admin_client.get("/api/v2/learner/content/scopes/test_scope/summary")
    assert response.status_code == 200
