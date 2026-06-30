"""API tests for content factory preview routes."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user, require_admin


class FakeSession:
    async def commit(self):
        return None


class FakeStagingPreviewService:
    async def preview_scope(self, session, scope_id, *, layers=None):
        from app.services.content_staging_preview_service import StagingPreviewReport
        return StagingPreviewReport(
            scope_id=scope_id,
            layers=layers or [],
            total_artifacts_count=0,
            active_artifacts_count=0,
            pending_artifacts_count=0,
            learner_visible_count=0,
            artifacts=[],
        )

    async def preview_caps_ref(self, session, scope_id, caps_ref, *, layers=None):
        from app.services.content_staging_preview_service import StagingCapsRefPreview
        return StagingCapsRefPreview(
            scope_id=scope_id,
            caps_ref=caps_ref,
            layers=layers or [],
            total_artifacts_count=0,
            active_artifacts_count=0,
            learner_visible_count=0,
            artifacts=[],
        )


class FakeLearnerReadService:
    async def get_scope_content_summary(self, session, scope_id):
        from app.services.content_learner_read_service import LearnerScopeContentSummary
        return LearnerScopeContentSummary(
            scope_id=scope_id,
            diagnostic_items_count=0,
            lessons_count=0,
            total_artifacts_count=0,
            last_promotion_at=None,
        )

    async def get_diagnostic_items(self, session, *, scope_id, caps_ref=None, limit=20):
        return []

    async def get_lessons(self, session, *, scope_id, caps_ref=None, limit=20):
        return []


def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


def _learner_user():
    return {"sub": str(uuid.uuid4()), "role": "learner", "type": "access"}


def _session():
    return FakeSession()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client():
    app.dependency_overrides[require_admin] = _admin_user
    app.dependency_overrides[content_factory.get_staging_preview_service] = FakeStagingPreviewService
    app.dependency_overrides[content_factory.get_learner_read_service] = FakeLearnerReadService
    app.dependency_overrides[content_factory.get_db] = _session
    return TestClient(app)


@pytest.fixture
def learner_client():
    app.dependency_overrides[get_current_user] = _learner_user
    app.dependency_overrides[content_factory.get_staging_preview_service] = FakeStagingPreviewService
    app.dependency_overrides[content_factory.get_learner_read_service] = FakeLearnerReadService
    app.dependency_overrides[content_factory.get_db] = _session
    return TestClient(app)


def test_unauthenticated_staging_preview_rejected(learner_client: TestClient) -> None:
    """Unauthenticated staging preview rejected."""
    app.dependency_overrides.clear()
    response = learner_client.get("/api/v2/admin/content-factory/staging-preview/scopes/test_scope")
    assert response.status_code == 401


def test_non_admin_cannot_fetch_staging_preview(learner_client: TestClient) -> None:
    """Non-admin cannot fetch staging preview."""
    response = learner_client.get("/api/v2/admin/content-factory/staging-preview/scopes/test_scope")
    assert response.status_code == 403


def test_admin_can_fetch_staging_preview(admin_client: TestClient) -> None:
    """Admin can fetch staging preview."""
    response = admin_client.get("/api/v2/admin/content-factory/staging-preview/scopes/test_scope")
    assert response.status_code == 200


def test_admin_can_fetch_staging_preview_by_caps_ref(admin_client: TestClient) -> None:
    """Admin can fetch staging preview by CAPS ref."""
    response = admin_client.get("/api/v2/admin/content-factory/staging-preview/scopes/test_scope/caps/test_ref")
    assert response.status_code == 200


def test_admin_can_fetch_production_preview(admin_client: TestClient) -> None:
    """Admin can fetch production preview."""
    response = admin_client.get("/api/v2/admin/content-factory/production-preview/scopes/test_scope")
    assert response.status_code == 200


def test_admin_can_fetch_production_preview_by_caps_ref(admin_client: TestClient) -> None:
    """Admin can fetch production preview by CAPS ref."""
    response = admin_client.get("/api/v2/admin/content-factory/production-preview/scopes/test_scope/caps/test_ref")
    assert response.status_code == 200


def test_non_admin_cannot_fetch_production_preview(learner_client: TestClient) -> None:
    """Non-admin cannot fetch production preview."""
    response = learner_client.get("/api/v2/admin/content-factory/production-preview/scopes/test_scope")
    assert response.status_code == 403


def test_staging_preview_is_under_admin(admin_client: TestClient) -> None:
    """Staging preview is under /admin."""
    response = admin_client.get("/api/v2/admin/content-factory/staging-preview/scopes/test_scope")
    assert response.status_code == 200
    assert "/admin/" in str(response.request.url)


def test_production_preview_is_under_admin(admin_client: TestClient) -> None:
    """Production preview is under /admin."""
    response = admin_client.get("/api/v2/admin/content-factory/production-preview/scopes/test_scope")
    assert response.status_code == 200
    assert "/admin/" in str(response.request.url)
