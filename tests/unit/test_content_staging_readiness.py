from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.models.content_factory import ContentArtifactStatus, ContentArtifactType, ContentLayer
from app.services.content_staging_readiness import ContentStagingReadinessService, StagingReadinessStatus


class _Result:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows


class _Session:
    def __init__(self, artifacts=None, sources=None):
        self.artifacts = artifacts or []
        self.sources = sources or []
        self.added = []

    async def execute(self, stmt):
        text = str(stmt)
        if "content_artifact_sources" in text:
            return _Result(self.sources)
        return _Result(self.artifacts)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        return None


def _artifact(status, *, caps_ref="4.M.1.1", layer=ContentLayer.DIAGNOSTIC_ITEMS, snapshot="snap-1"):
    artifact_id = uuid.uuid4()
    return SimpleNamespace(
        artifact_id=artifact_id,
        scope_id="grade4_mathematics_en",
        content_layer=layer,
        artifact_type=ContentArtifactType.DIAGNOSTIC_ITEM,
        caps_ref=caps_ref,
        status=status,
        source_snapshot_hash=snapshot,
    )


def _source(artifact, *, license_status="government_open", quality=0.9):
    return SimpleNamespace(
        artifact_id=artifact.artifact_id,
        source_document_id="doc-1",
        source_hash="source-hash",
        license_status=license_status,
        source_quality_score=quality,
    )


@pytest.mark.asyncio
async def test_all_configured_scopes_are_enumerated() -> None:
    report = await ContentStagingReadinessService().verify_all_scopes(_Session(), persist=False)

    assert [scope.scope_id for scope in report.scopes] == ["grade4_mathematics_en"]


@pytest.mark.asyncio
async def test_pending_review_creates_blocker_but_report_completes() -> None:
    pending = _artifact(ContentArtifactStatus.PENDING_REVIEW)
    report = await ContentStagingReadinessService().verify_scope(
        "grade4_mathematics_en",
        session=_Session([pending]),
    )

    assert report.status == StagingReadinessStatus.BLOCKED_BY_REVIEW
    assert report.can_seed_staging is False
    assert any(blocker.code == "pending_human_review" for blocker in report.blockers)


@pytest.mark.asyncio
async def test_approved_artifacts_make_scope_partially_stageable() -> None:
    approved = _artifact(ContentArtifactStatus.APPROVED)
    report = await ContentStagingReadinessService().verify_scope(
        "grade4_mathematics_en",
        session=_Session([approved], [_source(approved)]),
    )

    assert report.status == StagingReadinessStatus.PARTIALLY_STAGEABLE
    assert report.can_seed_staging is True
    assert report.can_promote_production is False


@pytest.mark.asyncio
async def test_red_coverage_creates_blocked_by_coverage() -> None:
    report = await ContentStagingReadinessService().verify_scope("grade4_mathematics_en", session=_Session())

    assert report.status == StagingReadinessStatus.BLOCKED_BY_COVERAGE
    assert any(blocker.code == "insufficient_approved_coverage" for blocker in report.blockers)


@pytest.mark.asyncio
async def test_invalid_provenance_excludes_artifact_from_stageable_count() -> None:
    approved = _artifact(ContentArtifactStatus.APPROVED, snapshot=None)
    report = await ContentStagingReadinessService().verify_scope(
        "grade4_mathematics_en",
        session=_Session([approved], [_source(approved)]),
    )

    assert report.can_seed_staging is False
    assert any(blocker.code == "invalid_provenance" for blocker in report.blockers)


@pytest.mark.asyncio
async def test_rejected_and_quarantined_artifacts_are_excluded_from_stageable_count() -> None:
    rejected = _artifact(ContentArtifactStatus.REJECTED)
    quarantined = _artifact(ContentArtifactStatus.QUARANTINED)
    report = await ContentStagingReadinessService().verify_scope(
        "grade4_mathematics_en",
        session=_Session([rejected, quarantined]),
    )

    assert report.summary["stageable"] == 0
    assert report.can_seed_staging is False


@pytest.mark.asyncio
async def test_production_promotion_remains_blocked_when_review_is_pending() -> None:
    approved = _artifact(ContentArtifactStatus.APPROVED)
    pending = _artifact(ContentArtifactStatus.PENDING_REVIEW)
    report = await ContentStagingReadinessService().verify_scope(
        "grade4_mathematics_en",
        session=_Session([approved, pending], [_source(approved)]),
    )

    assert report.can_seed_staging is True
    assert report.can_promote_production is False
    assert any(blocker.pending_review for blocker in report.blockers)


@pytest.mark.asyncio
async def test_verification_report_persists_blockers() -> None:
    session = _Session([_artifact(ContentArtifactStatus.PENDING_REVIEW)])
    report = await ContentStagingReadinessService().verify_all_scopes(session, actor_id="admin-1")

    assert report.run_id is not None
    assert len(session.added) == 2
    scope_result = session.added[1]
    assert scope_result.blockers_json
    assert scope_result.created_by is None or scope_result.created_by == "admin-1"
