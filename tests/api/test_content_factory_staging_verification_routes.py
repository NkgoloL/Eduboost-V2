from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user
from app.services.content_staging_readiness import (
    AllScopeStagingVerificationReport,
    ScopeBlocker,
    ScopeStagingVerificationReport,
    StagingReadinessStatus,
)

pytestmark = pytest.mark.unit


class FakeSession:
    async def commit(self):
        return None


class FakeReadinessService:
    async def verify_all_scopes(self, session, *, include_partial=True, actor_id=None, persist=True):
        return AllScopeStagingVerificationReport(
            run_id=uuid.uuid4(),
            status="completed",
            can_seed_staging=True,
            can_promote_production=False,
            created_by=actor_id,
            summary={"total_scopes": 1},
            scopes=[_scope_report()],
        )

    async def verify_scope(self, scope_id, *, session, include_partial=True, actor_id=None):
        if scope_id == "unknown_scope":
            return ScopeStagingVerificationReport(
                scope_id=scope_id,
                status=StagingReadinessStatus.BLOCKED_BY_MISSING_SCOPE,
                can_seed_staging=False,
                can_promote_production=False,
                blockers=[ScopeBlocker(code="missing_scope")],
            )
        return _scope_report(scope_id)

    async def list_runs(self, session, *, limit=20):
        return []

    async def get_run_report(self, session, run_id):
        return await self.verify_all_scopes(session, persist=False)


def _scope_report(scope_id="grade4_mathematics_en"):
    return ScopeStagingVerificationReport(
        scope_id=scope_id,
        status=StagingReadinessStatus.PARTIALLY_STAGEABLE,
        can_seed_staging=True,
        can_promote_production=False,
        blockers=[ScopeBlocker(code="pending_human_review", layer="diagnostic_items", caps_ref="4.M.1.1", required=40, approved=32, pending_review=8)],
        summary={"stageable": 32, "pending_review": 8},
    )


def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


def _parent_user():
    return {"sub": str(uuid.uuid4()), "role": "parent", "type": "access"}


def _fake_session():
    return FakeSession()


def _fake_readiness_service():
    return FakeReadinessService()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def _client():
    return TestClient(app, raise_server_exceptions=False)


def test_unauthenticated_all_scope_verification_rejected() -> None:
    response = _client().post("/api/v2/admin/content-factory/staging-verification/all-scopes")
    assert response.status_code == 401


def test_non_admin_all_scope_verification_rejected() -> None:
    app.dependency_overrides[get_current_user] = _parent_user
    response = _client().post("/api/v2/admin/content-factory/staging-verification/all-scopes")
    assert response.status_code == 403


def test_admin_can_run_all_scope_staging_verification() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_staging_readiness_service] = _fake_readiness_service

    response = _client().post("/api/v2/admin/content-factory/staging-verification/all-scopes")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "completed"
    assert data["can_seed_staging"] is True


def test_response_includes_all_configured_scopes() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_staging_readiness_service] = _fake_readiness_service

    response = _client().post("/api/v2/admin/content-factory/staging-verification/all-scopes")

    scopes = response.json()["data"]["scopes"]
    assert [scope["scope_id"] for scope in scopes] == ["grade4_mathematics_en"]


def test_pending_review_appears_as_blocker_not_500() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_staging_readiness_service] = _fake_readiness_service

    response = _client().post("/api/v2/admin/content-factory/staging-verification/all-scopes")

    assert response.status_code == 200
    blocker_codes = [blocker["code"] for blocker in response.json()["data"]["scopes"][0]["blockers"]]
    assert "pending_human_review" in blocker_codes


def test_scope_specific_readiness_works() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_staging_readiness_service] = _fake_readiness_service

    response = _client().get("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/staging-readiness")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "partially_stageable"


def test_unknown_scope_returns_404() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _fake_session
    app.dependency_overrides[content_factory.get_staging_readiness_service] = _fake_readiness_service

    response = _client().get("/api/v2/admin/content-factory/scopes/unknown_scope/staging-readiness")

    assert response.status_code == 404
