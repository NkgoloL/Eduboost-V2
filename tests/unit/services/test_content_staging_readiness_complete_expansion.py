import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentStagingVerificationRun,
    ContentStagingVerificationScopeResult,
)
from app.services.content_scope_registry import ContentScopeRegistry

from app.services.content_staging_readiness import (
    ContentStagingReadinessService,
    StagingReadinessStatus,
    BlockerSeverity,
    ScopeBlocker,
    LayerReadinessSummary,
    ScopeStagingVerificationReport,
    AllScopeStagingVerificationReport,
    _value,
)


def test_models_and_enums():
    assert StagingReadinessStatus.READY_FOR_STAGING.value == "ready_for_staging"
    assert BlockerSeverity.BLOCKING.value == "blocking"
    assert _value(StagingReadinessStatus.READY_FOR_STAGING) == "ready_for_staging"
    assert _value("plain_string") == "plain_string"

    blocker = ScopeBlocker(code="missing_scope", severity=BlockerSeverity.BLOCKING)
    assert blocker.code == "missing_scope"


@pytest.mark.asyncio
async def test_verify_scope_missing_scope():
    mock_registry = MagicMock(spec=ContentScopeRegistry)
    mock_registry.get_scope_targets.side_effect = LookupError("Scope not found")

    service = ContentStagingReadinessService(scope_registry=mock_registry)
    session = AsyncMock()

    report = await service.verify_scope("nonexistent_scope", session=session)
    assert report.status == StagingReadinessStatus.BLOCKED_BY_MISSING_SCOPE
    assert report.can_seed_staging is False
    assert report.can_promote_production is False
    assert any(b.code == "missing_scope" for b in report.blockers)


@pytest.mark.asyncio
async def test_verify_scope_all_layer_and_blocker_branches():
    mock_registry = MagicMock(spec=ContentScopeRegistry)

    # 4 targets with different layers and status outcomes
    target1 = MagicMock()
    target1.caps_ref = "4.M.1"
    target1.targets = {"lessons.approved": 2, "diagnostic_items.approved": 0}

    target2 = MagicMock()
    target2.caps_ref = "4.M.2"
    target2.targets = {"lessons.approved": 1}

    mock_registry.get_scope_targets.return_value = [target1, target2]

    service = ContentStagingReadinessService(scope_registry=mock_registry)
    session = AsyncMock()

    # Create artifacts
    art_approved = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="scope-1",
        caps_ref="4.M.1",
        content_layer="lessons",
        status=ContentArtifactStatus.APPROVED,
        source_snapshot_hash="snap-hash-1",
        artifact_json={},
        artifact_hash="h1",
    )
    src_valid = ContentArtifactSource(
        source_id=uuid.uuid4(),
        artifact_id=art_approved.artifact_id,
        source_document_id="doc-1",
        source_chunk_id="chunk-1",
        license_status="government_open",
        source_quality_score=0.9,
    )

    art_bad_prov = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="scope-1",
        caps_ref="4.M.1",
        content_layer="lessons",
        status=ContentArtifactStatus.APPROVED,
        source_snapshot_hash=None,  # Invalid provenance
        artifact_json={},
        artifact_hash="h2",
    )

    art_bad_lic = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="scope-1",
        caps_ref="4.M.1",
        content_layer="lessons",
        status=ContentArtifactStatus.APPROVED,
        source_snapshot_hash="snap-hash-3",
        artifact_json={},
        artifact_hash="h3",
    )
    src_bad_lic = ContentArtifactSource(
        source_id=uuid.uuid4(),
        artifact_id=art_bad_lic.artifact_id,
        source_document_id="doc-3",
        source_chunk_id="chunk-3",
        license_status="restricted",  # Invalid license
        source_quality_score=0.9,
    )

    art_low_qual = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="scope-1",
        caps_ref="4.M.1",
        content_layer="lessons",
        status=ContentArtifactStatus.APPROVED,
        source_snapshot_hash="snap-hash-4",
        artifact_json={},
        artifact_hash="h4",
    )
    src_low_qual = ContentArtifactSource(
        source_id=uuid.uuid4(),
        artifact_id=art_low_qual.artifact_id,
        source_document_id="doc-4",
        source_chunk_id="chunk-4",
        license_status="government_open",
        source_quality_score=0.3,  # Low quality < 0.5
    )

    # In 4.M.2, have pending review and validation failed
    art_pending = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        scope_id="scope-1",
        caps_ref="4.M.2",
        content_layer="lessons",
        status=ContentArtifactStatus.PENDING_REVIEW,
        artifact_json={},
        artifact_hash="h5",
    )

    artifacts = [art_approved, art_bad_prov, art_bad_lic, art_low_qual, art_pending]
    sources = [src_valid, src_bad_lic, src_low_qual]

    mock_res_art = MagicMock()
    mock_res_art.scalars.return_value.all.return_value = artifacts

    mock_res_src = MagicMock()
    mock_res_src.scalars.return_value.all.return_value = sources

    session.execute.side_effect = [mock_res_art, mock_res_src]

    report = await service.verify_scope("scope-1", session=session, include_partial=True)
    assert report.status in {StagingReadinessStatus.PARTIALLY_STAGEABLE, StagingReadinessStatus.BLOCKED_BY_PROVENANCE}
    assert report.can_seed_staging is True  # stageable > 0 and include_partial=True
    assert report.can_promote_production is False
    assert len(report.blockers) > 0

    # Also test get_scope_blockers
    session.execute.side_effect = [mock_res_art, mock_res_src]
    blockers = await service.get_scope_blockers("scope-1", session=session)
    assert len(blockers) == len(report.blockers)


@pytest.mark.asyncio
async def test_verify_all_scopes_and_persist(tmp_path):
    mock_registry = MagicMock(spec=ContentScopeRegistry)
    scope1 = MagicMock(scope_id="scope-1")
    scope2 = MagicMock(scope_id="scope-2")

    mock_registry.list_active_scopes.return_value = [scope1]
    mock_registry.list_scopes.return_value = [scope1, scope2]

    # Target configuration
    target = MagicMock()
    target.caps_ref = "4.M.1"
    target.targets = {"lessons.approved": 1}
    mock_registry.get_scope_targets.return_value = [target]

    service = ContentStagingReadinessService(scope_registry=mock_registry)
    session = AsyncMock()

    # Empty artifacts for both
    mock_res_art = MagicMock()
    mock_res_art.scalars.return_value.all.return_value = []
    session.execute.return_value = mock_res_art

    # 1. include_review_scopes=False, persist=True
    all_report = await service.verify_all_scopes(
        session,
        include_partial=True,
        actor_id="admin-1",
        persist=True,
        include_review_scopes=False,
    )
    assert all_report.status == "completed"
    assert len(all_report.scopes) == 1
    session.add.assert_called()
    session.flush.assert_called()

    # 2. include_review_scopes=True, persist=False
    all_report_rev = await service.verify_all_scopes(
        session,
        include_partial=False,
        actor_id="admin-1",
        persist=False,
        include_review_scopes=True,
    )
    assert len(all_report_rev.scopes) == 2


@pytest.mark.asyncio
async def test_list_runs_and_get_run_report():
    service = ContentStagingReadinessService()
    session = AsyncMock()

    run_id = uuid.uuid4()
    stored_run = ContentStagingVerificationRun(
        run_id=run_id,
        status="completed",
        summary_json={"total_scopes": 1},
        created_by="user-1",
        created_at=datetime.now(timezone.utc),
    )

    # 1. list_runs
    mock_list_res = MagicMock()
    mock_list_res.scalars.return_value.all.return_value = [stored_run]
    session.execute.return_value = mock_list_res

    runs = await service.list_runs(session, limit=10)
    assert len(runs) == 1
    assert runs[0].run_id == run_id

    # 2. get_run_report not found
    session.get.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.get_run_report(session, run_id)

    # 3. get_run_report found
    session.get.return_value = stored_run
    scope_result = ContentStagingVerificationScopeResult(
        run_id=run_id,
        scope_id="scope-1",
        status=StagingReadinessStatus.READY_FOR_STAGING.value,
        can_seed_staging=True,
        can_promote_production=True,
        summary_json={
            "target": 5,
            "approved": 5,
            "layers": [
                {
                    "layer": "lessons",
                    "caps_ref": "4.M.1",
                    "target": 5,
                    "approved": 5,
                    "pending_review": 0,
                    "generated": 0,
                    "validation_failed": 0,
                    "rejected": 0,
                    "quarantined": 0,
                    "seeded_staging": 0,
                    "promoted_production": 0,
                    "stageable": 5,
                    "invalid_provenance": 0,
                    "invalid_license": 0,
                    "low_source_quality": 0,
                    "status": StagingReadinessStatus.READY_FOR_STAGING.value,
                }
            ],
        },
        blockers_json=[],
    )

    mock_scope_res = MagicMock()
    mock_scope_res.scalars.return_value.all.return_value = [scope_result]
    session.execute.return_value = mock_scope_res

    report = await service.get_run_report(session, run_id)
    assert report.run_id == run_id
    assert len(report.scopes) == 1
    assert report.scopes[0].can_seed_staging is True
    assert report.scopes[0].status == StagingReadinessStatus.READY_FOR_STAGING


def test_scope_status_edge_hierarchy():
    service = ContentStagingReadinessService()

    # 1. No configured layers -> NOT_CONFIGURED
    l_unconfig = LayerReadinessSummary(
        layer="lessons",
        caps_ref="4.M.1",
        target=0,
        status=StagingReadinessStatus.NOT_CONFIGURED,
    )
    assert service._scope_status([l_unconfig], []) == StagingReadinessStatus.NOT_CONFIGURED

    # 2. All ready -> READY_FOR_STAGING
    l_ready = LayerReadinessSummary(
        layer="lessons",
        caps_ref="4.M.1",
        target=1,
        stageable=1,
        status=StagingReadinessStatus.READY_FOR_STAGING,
    )
    assert service._scope_status([l_ready], []) == StagingReadinessStatus.READY_FOR_STAGING

    # 3. Hierarchy checks
    l_prov = LayerReadinessSummary(
        layer="lessons",
        caps_ref="4.M.1",
        target=1,
        stageable=0,
        status=StagingReadinessStatus.BLOCKED_BY_PROVENANCE,
    )
    assert service._scope_status([l_prov], []) == StagingReadinessStatus.BLOCKED_BY_PROVENANCE

    l_lic = LayerReadinessSummary(
        layer="lessons",
        caps_ref="4.M.1",
        target=1,
        stageable=0,
        status=StagingReadinessStatus.BLOCKED_BY_LICENSE,
    )
    assert service._scope_status([l_lic], []) == StagingReadinessStatus.BLOCKED_BY_LICENSE
