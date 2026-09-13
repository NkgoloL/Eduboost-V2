import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentStagingArtifact,
    ContentStagingSeedItem,
)
from app.services.content_staging_preview_service import (
    ContentStagingPreviewService,
    StagingArtifactPreview,
    StagingPreviewReport,
    StagingCapsRefPreview,
)
from app.services.content_staging_read_verification import (
    ContentStagingReadVerificationService,
    StagingReadVerificationReport,
    ScopeStagingReadReport,
)


@pytest.mark.asyncio
async def test_content_staging_preview_service_preview_scope():
    service = ContentStagingPreviewService()
    session = AsyncMock()

    aid1 = uuid.uuid4()
    aid2 = uuid.uuid4()
    seed_run_id = uuid.uuid4()

    staging_art1 = MagicMock(spec=ContentStagingArtifact)
    staging_art1.artifact_id = aid1
    staging_art1.scope_id = "scope-1"
    staging_art1.caps_ref = "4.M.1"
    staging_art1.layer = "lessons"
    staging_art1.artifact_type = "lesson"
    staging_art1.staging_status = "active"
    staging_art1.created_by_seed_run_id = seed_run_id
    staging_art1.payload_json = {"title": "L1"}
    staging_art1.source_artifact_hash = "h1"
    staging_art1.created_at = datetime.now(timezone.utc)

    staging_art2 = MagicMock(spec=ContentStagingArtifact)
    staging_art2.artifact_id = aid2
    staging_art2.scope_id = "scope-1"
    staging_art2.caps_ref = "4.M.1"
    staging_art2.layer = "diagnostic_items"
    staging_art2.artifact_type = "diagnostic_item"
    staging_art2.staging_status = "pending"
    staging_art2.created_by_seed_run_id = None
    staging_art2.payload_json = {"question": "Q1"}
    staging_art2.source_artifact_hash = "h2"
    staging_art2.created_at = datetime.now(timezone.utc)

    gen_art1 = MagicMock(artifact_id=aid1)
    gen_art2 = MagicMock(artifact_id=aid2)

    # Mock query result
    mock_result = MagicMock()
    mock_result.__iter__.return_value = [
        (staging_art1, gen_art1),
        (staging_art2, gen_art2),
    ]
    session.execute.return_value = mock_result

    # Mock seed run status and verification status scalar queries
    session.scalar.side_effect = ["completed", "completed"]

    report = await service.preview_scope(session, "scope-1", layers=["lessons", "diagnostic_items"])
    assert report.scope_id == "scope-1"
    assert report.total_artifacts_count == 2
    assert report.active_artifacts_count == 1
    assert report.pending_artifacts_count == 1
    assert report.learner_visible_count == 0
    assert len(report.artifacts) == 2
    assert report.artifacts[0].learner_visible is False
    assert report.artifacts[0].verification_passed is True


@pytest.mark.asyncio
async def test_content_staging_preview_service_preview_caps_ref():
    service = ContentStagingPreviewService()
    session = AsyncMock()

    aid = uuid.uuid4()
    staging_art = MagicMock(spec=ContentStagingArtifact)
    staging_art.artifact_id = aid
    staging_art.scope_id = "scope-1"
    staging_art.caps_ref = "4.M.1"
    staging_art.layer = "lessons"
    staging_art.artifact_type = "lesson"
    staging_art.staging_status = "active"
    staging_art.created_by_seed_run_id = None
    staging_art.payload_json = {"title": "L1"}
    staging_art.source_artifact_hash = "h1"
    staging_art.created_at = datetime.now(timezone.utc)

    gen_art = MagicMock(artifact_id=aid)

    mock_result = MagicMock()
    mock_result.__iter__.return_value = [(staging_art, gen_art)]
    session.execute.return_value = mock_result

    report = await service.preview_caps_ref(session, "scope-1", "4.M.1", layers=["lessons"])
    assert report.scope_id == "scope-1"
    assert report.caps_ref == "4.M.1"
    assert report.total_artifacts_count == 1
    assert report.active_artifacts_count == 1
    assert report.learner_visible_count == 0


@pytest.mark.asyncio
async def test_content_staging_preview_status_helpers():
    service = ContentStagingPreviewService()
    session = AsyncMock()

    # 1. seed run status
    session.scalar.return_value = "running"
    assert await service._get_seed_run_status(session, "run-1") == "running"

    # 2. staging verification status: None
    session.scalar.return_value = None
    assert await service._get_staging_verification_status(session, "run-1") is None

    # 3. staging verification status: verified
    session.scalar.return_value = "verified"
    assert await service._get_staging_verification_status(session, "run-1") is True

    # 4. staging verification status: failed
    session.scalar.return_value = "failed"
    assert await service._get_staging_verification_status(session, "run-1") is False


@pytest.mark.asyncio
async def test_content_staging_read_verification_seed_run():
    service = ContentStagingReadVerificationService()
    session = AsyncMock()

    seed_run_id = uuid.uuid4()
    aid1 = uuid.uuid4()
    aid2 = uuid.uuid4()

    item1 = MagicMock(
        spec=ContentStagingSeedItem,
        artifact_id=aid1,
        scope_id="scope-1",
        caps_ref="4.M.1",
        layer="lessons",
    )
    item2 = MagicMock(
        spec=ContentStagingSeedItem,
        artifact_id=aid2,
        scope_id="scope-1",
        caps_ref="4.M.2",
        layer="lessons",
    )

    # Seed items query
    res_items = MagicMock()
    res_items.scalars.return_value.all.return_value = [item1, item2]

    # Staging row for item1: valid
    staging1 = MagicMock(
        staging_status="active",
        scope_id="scope-1",
        caps_ref="4.M.1",
        layer="lessons",
    )
    res_stg1 = MagicMock()
    res_stg1.scalars.return_value.all.return_value = [staging1]

    # Staging row for item2: empty (missing record)
    res_stg2 = MagicMock()
    res_stg2.scalars.return_value.all.return_value = []

    # Active staging count query: returns 1
    res_active = MagicMock()
    res_active.scalars.return_value.all.return_value = [staging1]

    session.execute.side_effect = [res_items, res_stg1, res_stg2, res_active]

    # Source artifact for item1: valid APPROVED
    src1 = MagicMock(status=ContentArtifactStatus.APPROVED)
    session.get.side_effect = [src1]

    report = await service.verify_seed_run(session, seed_run_id)
    assert report.passed is False
    assert report.verified_count == 1
    assert any("Missing staging record" in e for e in report.errors)
    assert any("does not match active staging count" in e for e in report.errors)


@pytest.mark.asyncio
async def test_content_staging_read_verification_seed_run_edge_errors():
    service = ContentStagingReadVerificationService()
    session = AsyncMock()

    seed_run_id = uuid.uuid4()
    aid = uuid.uuid4()
    item = MagicMock(
        spec=ContentStagingSeedItem,
        artifact_id=aid,
        scope_id="scope-1",
        caps_ref="4.M.1",
        layer="lessons",
    )

    # 1. Multiple staging records, inactive, mismatched scope/caps/layer, deleted source
    res_items = MagicMock()
    res_items.scalars.return_value.all.return_value = [item]

    bad_staging_1 = MagicMock(
        staging_status="inactive",
        scope_id="scope-other",
        caps_ref="4.M.other",
        layer="other_layer",
    )
    bad_staging_2 = MagicMock(staging_status="inactive")
    res_stg = MagicMock()
    res_stg.scalars.return_value.all.return_value = [bad_staging_1, bad_staging_2]

    res_active = MagicMock()
    res_active.scalars.return_value.all.return_value = [bad_staging_1]

    session.execute.side_effect = [res_items, res_stg, res_active]
    session.get.return_value = None  # Source deleted

    report = await service.verify_seed_run(session, seed_run_id)
    assert report.passed is False
    assert any("Multiple staging records" in e for e in report.errors)
    assert any("is not active" in e for e in report.errors)
    assert any("mismatched scope" in e for e in report.errors)
    assert any("mismatched caps_ref" in e for e in report.errors)
    assert any("mismatched layer" in e for e in report.errors)
    assert any("deleted" in e for e in report.errors)


@pytest.mark.asyncio
async def test_content_staging_read_verification_scope_staging():
    service = ContentStagingReadVerificationService()
    session = AsyncMock()

    aid1 = uuid.uuid4()
    aid2 = uuid.uuid4()
    aid3 = uuid.uuid4()

    stg1 = MagicMock(artifact_id=aid1)
    stg2 = MagicMock(artifact_id=aid2)
    stg3 = MagicMock(artifact_id=aid3)

    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [stg1, stg2, stg3]
    session.execute.return_value = mock_res

    # 1. stg1: source deleted (None)
    # 2. stg2: source in PENDING_REVIEW
    # 3. stg3: source in APPROVED
    src2 = MagicMock(status=ContentArtifactStatus.PENDING_REVIEW)
    src3 = MagicMock(status=ContentArtifactStatus.APPROVED)
    session.get.side_effect = [None, src2, src3]

    report = await service.verify_scope_staging(session, "scope-1", layers=["lessons"])
    assert report.scope_id == "scope-1"
    assert report.passed is False
    assert report.staged_artifacts_count == 2
    assert any("source missing" in e for e in report.errors)
    assert any("status is pending_review" in e for e in report.errors)
