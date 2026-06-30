"""Unit tests for content staging seed executor."""
from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.models.content_factory import ContentArtifactStatus, ContentLayer
from app.services.content_staging_seed_executor import ContentStagingSeedExecutor


class Factory:
    async def get_artifact_provenance(self, session, artifact_id):
        if str(artifact_id) == "00000000-0000-0000-0000-000000000000":
            return SimpleNamespace(passed=False)
        return SimpleNamespace(passed=True)


class Result:
    def __init__(self, items=None):
        self.items = items or []
    def scalars(self):
        return self
    def all(self):
        return self.items
    def scalar_one_or_none(self):
        return self.items[0] if self.items else None


class Session:
    def __init__(self, artifacts=None, overrides=None):
        self.artifacts = artifacts or []
        self.overrides = overrides or {}
        self.added = []
    async def get(self, model, key):
        return None
    async def execute(self, stmt):
        statement = str(stmt)
        if "content_validation_reports" in statement:
            return Result([SimpleNamespace(passed=True)])
        if "content_staging_artifacts" in statement:
            return Result([])
        return Result(self.artifacts)
    def add(self, obj):
        self.added.append(obj)
    async def flush(self):
        pass


def _artifact(status, artifact_id=None):
    return SimpleNamespace(
        artifact_id=artifact_id or uuid.uuid4(),
        scope_id="some_scope",
        status=status,
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        artifact_type="diagnostic_item",
        caps_ref="test",
        artifact_json={},
        artifact_hash="hash",
    )


@pytest.mark.asyncio
async def test_dry_run_lists_approved_seedable_artifacts():
    session = Session(artifacts=[_artifact(ContentArtifactStatus.APPROVED)])
    executor = ContentStagingSeedExecutor(factory_service=Factory())
    plan = await executor.dry_run_seed(session, "some_scope")
    assert len(plan.seedable) == 1
    assert len(plan.skipped) == 0


@pytest.mark.asyncio
async def test_pending_review_artifacts_are_skipped():
    session = Session(artifacts=[_artifact(ContentArtifactStatus.PENDING_REVIEW)])
    executor = ContentStagingSeedExecutor(factory_service=Factory())
    plan = await executor.dry_run_seed(session, "some_scope")
    assert len(plan.seedable) == 0
    assert len(plan.skipped) == 1
    assert "pending review" in plan.skipped[0].reason


@pytest.mark.asyncio
async def test_invalid_provenance_artifacts_are_skipped():
    artifact_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    session = Session(artifacts=[_artifact(ContentArtifactStatus.APPROVED, artifact_id=artifact_id)])
    executor = ContentStagingSeedExecutor(factory_service=Factory())
    plan = await executor.dry_run_seed(session, "some_scope")
    assert len(plan.seedable) == 0
    assert len(plan.skipped) == 1
    assert "provenance" in plan.skipped[0].reason.lower()


@pytest.mark.asyncio
async def test_valid_approved_artifact_creates_seed_item():
    art = _artifact(ContentArtifactStatus.APPROVED)
    session = Session(artifacts=[art])
    executor = ContentStagingSeedExecutor(factory_service=Factory())
    res = await executor.seed_staging(session, "some_scope", actor_id="admin")
    assert res.seeded_count == 1
    assert res.skipped_count == 0
    # The session had objects added (ContentSeedRun, ContentStagingSeedItem, etc)
    assert len(session.added) == 3
