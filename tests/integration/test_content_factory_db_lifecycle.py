"""tests/integration/test_content_factory_db_lifecycle.py
─────────────────────────────────────────────────────────────────────────────
DB-backed lifecycle tests for the Content Factory service layer.

Verifies that:
  - ContentFactoryService creates artifacts + provenance + validation reports
  - Artifacts without provenance enter VALIDATION_FAILED and cannot be approved
  - Artifacts with valid provenance enter PENDING_REVIEW and can be approved
  - ContentGenerationRunService.create_tasks_for_run is fully idempotent
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAction,
    ContentValidationReport,
    ContentGenerationTask,
)
from app.services.content_factory import ContentFactoryService
from app.services.content_generation_runs import ContentGenerationRunService
from app.domain.content_coverage import ContentLayer as DomainLayer

pytestmark = pytest.mark.integration

# ── helpers ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(autouse=True)
async def seed_content_scope(db_session):
    """Seed default content scope for foreign keys."""
    from app.models.content_factory import ContentScope, ContentScopeStatus
    scope = ContentScope(
        scope_id="grade4_mathematics_en",
        grade=4,
        subject_code="M",
        subject_slug="mathematics",
        subject_display_name="Mathematics",
        language="en",
        curriculum="CAPS",
        status=ContentScopeStatus.ACTIVE,
        source_policy={},
        targets={},
    )
    db_session.add(scope)
    await db_session.flush()


def _valid_source(caps_ref: str = "4.M.1.1") -> dict:
    return {
        "source_document_id": f"doc-{uuid.uuid4().hex[:8]}",
        "source_chunk_id": f"chunk-{uuid.uuid4().hex[:8]}",
        "caps_ref": caps_ref,
        "document_status": "approved",
        "license_status": "government_open",
        "chunk_quality_score": 0.9,
    }


def _artifact_payload(
    *,
    scope_id: str = "grade4_mathematics_en",
    caps_ref: str = "4.M.1.1",
    artifact_type: str = "lesson",
    sources: list[dict] | None = None,
    answer_key: dict | None = None,
) -> dict:
    payload: dict = {
        "scope_id": scope_id,
        "content_layer": "lessons",
        "artifact_type": artifact_type,
        "caps_ref": caps_ref,
        "grade": 4,
        "subject_code": "M",
        "language": "en",
        "artifact_json": {
            "title": "Place Value – Tens",
            "content": "A lesson on place value.",
            "safety_status": "passed",
        },
        "sources": sources if sources is not None else [_valid_source(caps_ref)],
    }
    if answer_key:
        payload["artifact_json"]["answer_key"] = answer_key
    return payload


# ── artifact creation lifecycle ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_artifact_with_valid_provenance_enters_pending_review(db_session):
    """Artifact with an approved source enters PENDING_REVIEW status."""
    service = ContentFactoryService()
    artifact = await service.create_artifact(db_session, payload=_artifact_payload())
    await db_session.flush()

    assert artifact.artifact_id is not None
    status_val = artifact.status.value if hasattr(artifact.status, "value") else artifact.status
    assert status_val == ContentArtifactStatus.PENDING_REVIEW.value

    # Validation report must exist and be passing
    result = await db_session.execute(
        select(ContentValidationReport).where(
            ContentValidationReport.artifact_id == artifact.artifact_id
        )
    )
    reports = list(result.scalars().all())
    assert len(reports) >= 1
    assert reports[-1].passed is True


@pytest.mark.asyncio
async def test_create_artifact_without_sources_enters_validation_failed(db_session):
    """Artifact without source citations is rejected at the validation gate."""
    service = ContentFactoryService()
    artifact = await service.create_artifact(
        db_session, payload=_artifact_payload(sources=[])
    )
    await db_session.flush()

    status_val = artifact.status.value if hasattr(artifact.status, "value") else artifact.status
    assert status_val == ContentArtifactStatus.VALIDATION_FAILED.value

    result = await db_session.execute(
        select(ContentValidationReport).where(
            ContentValidationReport.artifact_id == artifact.artifact_id
        )
    )
    reports = list(result.scalars().all())
    assert not reports[-1].passed
    assert any("ETL source" in e for e in reports[-1].errors)


@pytest.mark.asyncio
async def test_validation_failed_artifact_cannot_be_approved(db_session):
    """VALIDATION_FAILED artifacts are blocked from approval."""
    service = ContentFactoryService()
    artifact = await service.create_artifact(
        db_session, payload=_artifact_payload(sources=[])
    )
    await db_session.flush()

    with pytest.raises(ValueError, match="pending_review"):
        await service.review_artifact(
            db_session,
            artifact_id=artifact.artifact_id,
            reviewer_id="reviewer-1",
            review_action=ContentReviewAction.APPROVE,
        )


@pytest.mark.asyncio
async def test_pending_review_artifact_can_be_approved(db_session):
    """PENDING_REVIEW artifacts with sources can be approved."""
    service = ContentFactoryService()
    artifact = await service.create_artifact(db_session, payload=_artifact_payload())
    await db_session.flush()

    review = await service.review_artifact(
        db_session,
        artifact_id=artifact.artifact_id,
        reviewer_id="reviewer-1",
        review_action=ContentReviewAction.APPROVE,
        quality_score=0.95,
    )
    await db_session.flush()

    assert review.review_id is not None
    action_val = review.review_action.value if hasattr(review.review_action, "value") else review.review_action
    assert action_val == ContentReviewAction.APPROVE.value

    # Re-fetch artifact and verify status
    refreshed = await db_session.get(ContentGenerationArtifact, artifact.artifact_id)
    status_val = refreshed.status.value if hasattr(refreshed.status, "value") else refreshed.status
    assert status_val == ContentArtifactStatus.APPROVED.value


@pytest.mark.asyncio
async def test_diagnostic_item_requires_answer_key_for_validation(db_session):
    """diagnostic_item artifact without answer_key enters VALIDATION_FAILED."""
    service = ContentFactoryService()
    artifact = await service.create_artifact(
        db_session,
        payload=_artifact_payload(artifact_type="diagnostic_item"),
    )
    await db_session.flush()

    status_val = artifact.status.value if hasattr(artifact.status, "value") else artifact.status
    assert status_val == ContentArtifactStatus.VALIDATION_FAILED.value

    result = await db_session.execute(
        select(ContentValidationReport).where(
            ContentValidationReport.artifact_id == artifact.artifact_id
        )
    )
    reports = list(result.scalars().all())
    assert any("answer_key" in e for e in reports[-1].errors)


# ── generation run idempotency ────────────────────────────────────────────────

class _FakeRegistry:
    """Minimal ContentScopeRegistry stand-in that avoids the scope JSON files."""

    def validate_scope_exists(self, scope_id: str) -> None:
        if scope_id != "grade4_mathematics_en":
            raise LookupError(scope_id)

    def get_scope_caps_refs(self, scope_id: str) -> list[str]:
        return ["4.M.1.1", "4.M.1.2", "4.M.1.3"]


@pytest.mark.asyncio
async def test_create_tasks_for_run_is_idempotent(db_session):
    """Calling create_tasks_for_run twice for the same run does not duplicate tasks."""
    service = ContentGenerationRunService(_FakeRegistry())

    run = await service.create_run(
        db_session,
        scope_id="grade4_mathematics_en",
        layers=[DomainLayer.DIAGNOSTIC_ITEMS],
        requested_by="admin-test",
    )
    await db_session.flush()

    tasks_first = await service.create_tasks_for_run(db_session, run.run_id)
    await db_session.flush()
    tasks_second = await service.create_tasks_for_run(db_session, run.run_id)

    assert len(tasks_first) == 3  # one per caps_ref
    assert len(tasks_second) == 3
    assert {t.task_id for t in tasks_first} == {t.task_id for t in tasks_second}


@pytest.mark.asyncio
async def test_cancel_run_sets_queued_tasks_to_cancelled(db_session):
    """Cancelling a run marks all queued tasks as cancelled."""
    service = ContentGenerationRunService(_FakeRegistry())

    run = await service.create_run(
        db_session,
        scope_id="grade4_mathematics_en",
        layers=[DomainLayer.DIAGNOSTIC_ITEMS],
        requested_by="admin-test",
        dry_run=False,
    )
    await db_session.flush()
    await service.create_tasks_for_run(db_session, run.run_id)
    await db_session.flush()

    cancelled_run = await service.cancel_run(db_session, run.run_id, "admin-test")
    await db_session.flush()

    assert cancelled_run.status == "cancelled"

    result = await db_session.execute(
        select(ContentGenerationTask).where(
            ContentGenerationTask.run_id == run.run_id
        )
    )
    tasks = list(result.scalars().all())
    assert all(t.status == "cancelled" for t in tasks)
