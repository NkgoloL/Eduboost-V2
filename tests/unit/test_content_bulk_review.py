from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_bulk_review import ContentBulkReviewService
from app.services.content_review_risk import ReviewRisk


class Factory:
    def __init__(self, artifact):
        self.artifact = artifact
    async def get_artifact(self, session, artifact_id):
        return self.artifact


class Queue:
    def __init__(self, *, provenance=True, validation=True, risk="low"):
        self.provenance = provenance
        self.validation = validation
        self.risk = risk
    async def get_artifact_review_bundle(self, session, artifact_id):
        return SimpleNamespace(provenance={"passed": self.provenance}, validation_report={"passed": self.validation}, review_risk=ReviewRisk(self.risk, 0, []))


class Lifecycle:
    def __init__(self):
        self.approved = []
        self.rejected = []
        self.quarantined = []
    async def reject_artifact(self, session, artifact_id, actor_id, reason):
        self.rejected.append(artifact_id)
        session.add(SimpleNamespace(kind="review", artifact_id=artifact_id, reason=reason))
        return SimpleNamespace(artifact_id=artifact_id)
    async def quarantine_artifact(self, session, artifact_id, actor_id, reason):
        self.quarantined.append(artifact_id)
        return SimpleNamespace(artifact_id=artifact_id)


class Session:
    def __init__(self):
        self.added = []
    def add(self, obj):
        self.added.append(obj)


def _artifact(status=ContentArtifactStatus.PENDING_REVIEW):
    return SimpleNamespace(artifact_id=uuid.uuid4(), status=status)


@pytest.mark.asyncio
async def test_bulk_approve_rejects_high_risk_artifacts() -> None:
    artifact = _artifact()
    service = ContentBulkReviewService(lifecycle_service=Lifecycle(), factory_service=Factory(artifact), queue_service=Queue(risk="high"))

    with pytest.raises(ValueError, match="Bulk approval is disabled"):
        await service.bulk_approve(Session(), [artifact.artifact_id], reviewer_id="admin", notes="reviewed")


@pytest.mark.asyncio
async def test_bulk_approve_rejects_invalid_provenance() -> None:
    artifact = _artifact()
    service = ContentBulkReviewService(lifecycle_service=Lifecycle(), factory_service=Factory(artifact), queue_service=Queue(provenance=False))

    with pytest.raises(ValueError, match="Bulk approval is disabled"):
        await service.bulk_approve(Session(), [artifact.artifact_id], reviewer_id="admin", notes="reviewed")


@pytest.mark.asyncio
async def test_bulk_approve_enforces_max_batch_size(monkeypatch) -> None:
    monkeypatch.setenv("CONTENT_REVIEW_BULK_APPROVE_MAX", "1")
    artifact = _artifact()
    service = ContentBulkReviewService(lifecycle_service=Lifecycle(), factory_service=Factory(artifact), queue_service=Queue())

    with pytest.raises(ValueError, match="Bulk approval is disabled"):
        await service.bulk_approve(Session(), [artifact.artifact_id, uuid.uuid4()], reviewer_id="admin", notes="reviewed")


@pytest.mark.asyncio
async def test_bulk_approve_requires_notes() -> None:
    artifact = _artifact()
    service = ContentBulkReviewService(lifecycle_service=Lifecycle(), factory_service=Factory(artifact), queue_service=Queue())

    with pytest.raises(ValueError, match="Bulk approval is disabled"):
        await service.bulk_approve(Session(), [artifact.artifact_id], reviewer_id="admin", notes="")


@pytest.mark.asyncio
async def test_bulk_reject_writes_review_audit_events() -> None:
    artifact = _artifact()
    lifecycle = Lifecycle()
    session = Session()
    service = ContentBulkReviewService(lifecycle_service=lifecycle, factory_service=Factory(artifact), queue_service=Queue())

    result = await service.bulk_reject(session, [artifact.artifact_id], reviewer_id="admin", reason="bad source")

    assert result.status == "rejected"
    assert lifecycle.rejected == [artifact.artifact_id]
    assert session.added
