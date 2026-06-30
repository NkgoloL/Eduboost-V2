from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_routers import content_factory
from app.core.security import get_current_user
from app.services.content_bulk_review import BulkReviewResult
from app.services.content_review_queue import ArtifactReviewBundle, ReviewQueueItem, ReviewQueuePage, ReviewSummary
from app.services.content_review_risk import ReviewRisk

pytestmark = pytest.mark.unit


class FakeSession:
    async def commit(self):
        return None


class QueueService:
    async def list_queue(self, *args, **kwargs):
        return ReviewQueuePage(items=[ReviewQueueItem(artifact_id=uuid.uuid4(), scope_id="grade4_mathematics_en", content_layer="diagnostic_items", artifact_type="diagnostic_item", caps_ref="4.M.1.1", status="pending_review", risk_level="low", risk_reasons=[], validation_status="passed", provenance_status="passed")], total=1, limit=50, offset=0)
    async def get_review_summary(self, *args, **kwargs):
        return ReviewSummary(pending_review=1, low_risk=1)
    async def get_artifact_review_bundle(self, *args, **kwargs):
        return ArtifactReviewBundle(artifact={"artifact_id": str(uuid.uuid4())}, validation_report={"passed": True}, provenance={"passed": True}, sources=[{"source_chunk_id": "chunk"}], review_risk=ReviewRisk("low", 0, []), generation_metadata={})


class AssignmentService:
    async def assign_artifact(self, session, artifact_id, reviewer_id, assigned_by, priority="normal"):
        return SimpleNamespace(id=uuid.uuid4(), artifact_id=artifact_id, assigned_to=reviewer_id, assigned_by=assigned_by, priority=priority, status="assigned", due_by=None)
    async def assign_batch(self, *args, **kwargs):
        return []
    async def list_assignments(self, *args, **kwargs):
        return []
    async def get_reviewer_workload(self, session, reviewer_id):
        return SimpleNamespace(reviewer_id=reviewer_id, assigned=1, in_review=0, overdue=0, total_open=1)


class BulkService:
    async def bulk_assign(self, *args, **kwargs):
        return BulkReviewResult(status="assigned", artifact_ids=[uuid.uuid4()], summary={"assigned": 1})
    async def bulk_approve(self, *args, **kwargs):
        raise ValueError("Bulk approval blocked by invalid provenance.")
    async def bulk_reject(self, *args, **kwargs):
        return BulkReviewResult(status="rejected", artifact_ids=[uuid.uuid4()], summary={"rejected": 1})
    async def bulk_quarantine(self, *args, **kwargs):
        return BulkReviewResult(status="quarantined", artifact_ids=[uuid.uuid4()], summary={"quarantined": 1})


def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


def _parent_user():
    return {"sub": str(uuid.uuid4()), "role": "parent", "type": "access"}


def _session():
    return FakeSession()


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def _wire_admin():
    app.dependency_overrides[get_current_user] = _admin_user
    app.dependency_overrides[content_factory.get_db] = _session
    app.dependency_overrides[content_factory.get_content_review_queue_service] = lambda: QueueService()
    app.dependency_overrides[content_factory.get_content_reviewer_assignment_service] = lambda: AssignmentService()
    app.dependency_overrides[content_factory.get_content_bulk_review_service] = lambda: BulkService()


def _client():
    return TestClient(app, raise_server_exceptions=False)


def test_unauthenticated_review_queue_rejected() -> None:
    assert _client().get("/api/v2/admin/content-factory/review-queue").status_code == 401


def test_non_admin_review_queue_rejected() -> None:
    app.dependency_overrides[get_current_user] = _parent_user
    assert _client().get("/api/v2/admin/content-factory/review-queue").status_code == 403


def test_admin_can_list_review_queue() -> None:
    _wire_admin()
    response = _client().get("/api/v2/admin/content-factory/review-queue")
    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["status"] == "pending_review"


def test_admin_can_fetch_review_bundle() -> None:
    _wire_admin()
    response = _client().get(f"/api/v2/admin/content-factory/artifacts/{uuid.uuid4()}/review-bundle")
    assert response.status_code == 200
    assert response.json()["data"]["provenance"]["passed"] is True


def test_admin_can_assign_reviewer() -> None:
    _wire_admin()
    response = _client().post("/api/v2/admin/content-factory/review-assignments", json={"artifact_id": str(uuid.uuid4()), "reviewer_id": "reviewer-1"})
    assert response.status_code == 200
    assert response.json()["data"]["assigned_to"] == "reviewer-1"


def test_admin_can_bulk_assign() -> None:
    _wire_admin()
    response = _client().post("/api/v2/admin/content-factory/review-assignments/bulk", json={"artifact_ids": [str(uuid.uuid4())], "reviewer_id": "reviewer-1"})
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "assigned"


def test_admin_can_view_reviewer_workload() -> None:
    _wire_admin()
    response = _client().get("/api/v2/admin/content-factory/reviewers/reviewer-1/workload")
    assert response.status_code == 200
    assert response.json()["data"]["total_open"] == 1


def test_bulk_approve_blocks_invalid_artifact() -> None:
    _wire_admin()
    response = _client().post("/api/v2/admin/content-factory/review/bulk-approve", json={"artifact_ids": [str(uuid.uuid4())], "notes": "reviewed"})
    assert response.status_code == 409


def test_bulk_reject_works_with_reason() -> None:
    _wire_admin()
    response = _client().post("/api/v2/admin/content-factory/review/bulk-reject", json={"artifact_ids": [str(uuid.uuid4())], "reason": "bad source"})
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "rejected"


def test_openapi_contains_review_acceleration_endpoints() -> None:
    paths = app.openapi()["paths"]
    assert "/api/v2/admin/content-factory/review-queue" in paths
    assert "/api/v2/admin/content-factory/review/bulk-approve" in paths
