from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.services.content_review_queue import ContentReviewQueueService
from app.services.content_review_risk import ReviewRisk


class Result:
    def __init__(self, rows=None, count=0):
        self.rows = rows or []
        self.count = count
    def scalars(self):
        return self
    def all(self):
        return self.rows
    def scalar_one(self):
        return self.count


class Session:
    def __init__(self, artifacts=None):
        self.artifacts = artifacts or []
        self.calls = 0
    async def execute(self, stmt):
        self.calls += 1
        if self.calls == 1:
            return Result(self.artifacts)
        if self.calls in {2, 3}:
            return Result([])
        return Result(count=len(self.artifacts))


class Factory:
    async def get_artifact_provenance(self, session, artifact_id):
        return SimpleNamespace(passed=True, errors=[], source_snapshot_hash="snap", sources=[{"source_chunk_id": "chunk"}])
    async def get_artifact(self, session, artifact_id):
        return session.artifacts[0]


class Risk:
    def score_artifact(self, *args, **kwargs):
        return ReviewRisk(level="low", score=0, reasons=[])


def _artifact(**kwargs):
    data = {
        "artifact_id": uuid.uuid4(),
        "scope_id": "grade4_mathematics_en",
        "content_layer": "diagnostic_items",
        "artifact_type": "diagnostic_item",
        "caps_ref": "4.M.1.1",
        "status": "pending_review",
        "artifact_json": {"question": "?"},
        "provider": "deterministic",
        "model": "deterministic",
        "prompt_version": "v1",
        "run_id": None,
        "task_id": None,
        "created_at": None,
        "reviews": [],
    }
    data.update(kwargs)
    return SimpleNamespace(**data)


@pytest.mark.asyncio
async def test_queue_lists_only_pending_review_artifacts_by_default() -> None:
    artifact = _artifact()
    page = await ContentReviewQueueService(risk_service=Risk(), factory_service=Factory()).list_queue(Session([artifact]))

    assert page.total == 1
    assert page.items[0].status == "pending_review"


@pytest.mark.asyncio
async def test_queue_filters_by_scope_layer_caps_ref() -> None:
    artifact = _artifact(scope_id="grade4_mathematics_en", content_layer="lessons", caps_ref="4.M.1.1")
    page = await ContentReviewQueueService(risk_service=Risk(), factory_service=Factory()).list_queue(Session([artifact]), scope_id="grade4_mathematics_en", layer="lessons", caps_ref="4.M.1.1")

    assert page.items[0].content_layer == "lessons"
    assert page.items[0].caps_ref == "4.M.1.1"


@pytest.mark.asyncio
async def test_review_bundle_includes_artifact_validation_provenance_and_sources() -> None:
    artifact = _artifact()
    service = ContentReviewQueueService(risk_service=Risk(), factory_service=Factory())
    async def latest(session, ids):
        return {artifact.artifact_id: SimpleNamespace(validation_report_id=uuid.uuid4(), passed=True, checks={}, errors=[])}
    service._latest_validation_reports = latest
    bundle = await service.get_artifact_review_bundle(Session([artifact]), artifact.artifact_id)

    assert bundle.artifact["artifact_id"] == str(artifact.artifact_id)
    assert bundle.validation_report["passed"] is True
    assert bundle.provenance["passed"] is True
    assert bundle.sources
