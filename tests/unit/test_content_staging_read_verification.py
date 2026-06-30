"""Unit tests for content staging read verification."""
from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_staging_read_verification import ContentStagingReadVerificationService


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
    def __init__(self, seeded_items=None, staging_artifacts=None, sources=None):
        self.seeded_items = seeded_items or []
        self.staging_artifacts = staging_artifacts or []
        self.sources = sources or {}

    async def execute(self, stmt):
        stmt_str = str(stmt)
        if "content_staging_seed_items" in stmt_str:
            return Result(self.seeded_items)
        if "content_staging_artifacts" in stmt_str:
            return Result(self.staging_artifacts)
        return Result([])

    async def get(self, model, key):
        return self.sources.get(key)


@pytest.mark.asyncio
async def test_verification_fails_if_staging_record_is_missing():
    art_id = uuid.uuid4()
    run_id = uuid.uuid4()
    item = SimpleNamespace(artifact_id=art_id, seed_run_id=run_id, status="seeded")
    session = Session(seeded_items=[item], staging_artifacts=[])

    svc = ContentStagingReadVerificationService()
    report = await svc.verify_seed_run(session, run_id)

    assert not report.passed
    assert report.verified_count == 0
    assert any("Missing staging record" in err for err in report.errors)


@pytest.mark.asyncio
async def test_verification_fails_if_staged_artifact_is_not_approved():
    art_id = uuid.uuid4()
    run_id = uuid.uuid4()
    item = SimpleNamespace(artifact_id=art_id, seed_run_id=run_id, status="seeded")
    stag = SimpleNamespace(artifact_id=art_id, staging_status="active")
    source = SimpleNamespace(status=ContentArtifactStatus.PENDING_REVIEW)
    session = Session(seeded_items=[item], staging_artifacts=[stag], sources={art_id: source})

    svc = ContentStagingReadVerificationService()
    report = await svc.verify_seed_run(session, run_id)

    assert not report.passed
    assert any("invalid for staging" in err for err in report.errors)


@pytest.mark.asyncio
async def test_verification_passes_when_staged_records_match_seed_run():
    art_id = uuid.uuid4()
    run_id = uuid.uuid4()
    item = SimpleNamespace(artifact_id=art_id, seed_run_id=run_id, status="seeded")
    stag = SimpleNamespace(artifact_id=art_id, staging_status="active")
    source = SimpleNamespace(status=ContentArtifactStatus.APPROVED)
    session = Session(seeded_items=[item], staging_artifacts=[stag], sources={art_id: source})

    svc = ContentStagingReadVerificationService()
    report = await svc.verify_seed_run(session, run_id)

    assert report.passed
    assert report.verified_count == 1
    assert not report.errors
