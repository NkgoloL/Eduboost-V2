from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentStagingArtifact,
    ContentStagingSeedItem,
    ContentStagingVerificationRun,
    ContentStagingVerificationScopeResult,
)

from app.services.content_staging_read_verification import (
    ContentStagingReadVerificationService,
    ScopeStagingReadReport,
    StagingReadVerificationReport,
)
from app.services.content_staging_readiness import (
    AllScopeStagingVerificationReport,
    BlockerSeverity,
    ContentStagingReadinessService,
    LayerReadinessSummary,
    ScopeBlocker,
    ScopeStagingVerificationReport,
    StagingReadinessStatus,
    _value,
)


@pytest.mark.asyncio
async def test_content_staging_read_verification():
    service = ContentStagingReadVerificationService()
    session = AsyncMock()
    session.execute = AsyncMock()

    run_id = uuid.uuid4()
    art_id = uuid.uuid4()

    # 1. verify_seed_run clean pass
    item = ContentStagingSeedItem(
        id=uuid.uuid4(),
        seed_run_id=run_id,
        artifact_id=art_id,
        status="seeded",
        scope_id="scope_math_g4",
        caps_ref="4.M.1.1",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        target_table="diagnostic_items",
    )

    staging_art = ContentStagingArtifact(
        id=uuid.uuid4(),
        created_by_seed_run_id=run_id,
        artifact_id=art_id,
        staging_status="active",
        scope_id="scope_math_g4",
        caps_ref="4.M.1.1",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={"test": "payload"},
    )
    source_art = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.APPROVED,
    )

    items_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item]))))
    staging_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art]))))
    active_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art]))))

    session.execute.side_effect = [items_res, staging_res, active_res]
    session.get.return_value = source_art

    report = await service.verify_seed_run(session, run_id)
    assert isinstance(report, StagingReadVerificationReport)
    assert report.passed is True
    assert report.verified_count == 1
    assert len(report.errors) == 0

    # 2. verify_seed_run with multiple errors (missing staging, mismatched metadata, source deleted/unapproved)
    staging_mismatch = ContentStagingArtifact(
        id=uuid.uuid4(),
        created_by_seed_run_id=run_id,
        artifact_id=art_id,
        staging_status="inactive",
        scope_id="other_scope",
        caps_ref="other_ref",
        layer="lessons",
        artifact_type="lesson",
        payload_json={},
    )
    bad_staging_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_mismatch, staging_mismatch]))))
    session.execute.side_effect = [items_res, bad_staging_res, active_res]
    session.get.return_value = None  # source deleted

    fail_report = await service.verify_seed_run(session, run_id)
    assert fail_report.passed is False
    assert any("Multiple staging records" in e for e in fail_report.errors)
    assert any("not active" in e for e in fail_report.errors)
    assert any("mismatched scope" in e for e in fail_report.errors)
    assert any("deleted" in e for e in fail_report.errors)

    # 3. verify_scope_staging clean
    scope_staging_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art]))))
    session.execute.side_effect = None
    session.execute.return_value = scope_staging_res
    session.get.return_value = source_art

    scope_report = await service.verify_scope_staging(session, "scope_math_g4", layers=["diagnostic_items"])
    assert isinstance(scope_report, ScopeStagingReadReport)
    assert scope_report.passed is True
    assert scope_report.staged_artifacts_count == 1

    # 4. verify_scope_staging with unapproved source
    bad_source = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.PENDING_REVIEW,
    )
    session.get.return_value = bad_source
    scope_bad_report = await service.verify_scope_staging(session, "scope_math_g4")
    assert scope_bad_report.passed is False
    assert any("status is pending_review" in e for e in scope_bad_report.errors)


@pytest.mark.asyncio
async def test_content_staging_readiness_service():
    scope_registry = MagicMock()
    mock_scope = MagicMock(scope_id="scope_math_g4")
    scope_registry.list_scopes.return_value = [mock_scope]
    scope_registry.list_active_scopes.return_value = [mock_scope]

    target_mock = MagicMock(caps_ref="4.M.1.1", targets={"diagnostic_items.approved": 2, "lessons.approved": 0})
    scope_registry.get_scope_targets.return_value = [target_mock]




    service = ContentStagingReadinessService(scope_registry=scope_registry)
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()

    art_id1 = uuid.uuid4()
    art1 = ContentGenerationArtifact(
        artifact_id=art_id1,
        scope_id="scope_math_g4",
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        status=ContentArtifactStatus.APPROVED,
        source_snapshot_hash="hash_abc",
    )
    art_id2 = uuid.uuid4()
    art2 = ContentGenerationArtifact(
        artifact_id=art_id2,
        scope_id="scope_math_g4",
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        status=ContentArtifactStatus.APPROVED,
        source_snapshot_hash="hash_xyz",
    )


    src1 = ContentArtifactSource(
        source_id=uuid.uuid4(),
        artifact_id=art_id1,
        source_hash="s_hash",
        license_status="open",
        source_quality_score=0.9,
    )
    src2 = ContentArtifactSource(
        source_id=uuid.uuid4(),
        artifact_id=art_id2,
        source_hash="s_hash",
        license_status="restricted",  # invalid license
        source_quality_score=0.2,     # low quality
    )

    service._load_scope_artifacts = AsyncMock(return_value=[art1, art2])
    service._load_source_index = AsyncMock(return_value={
        art_id1: [src1],
        art_id2: [src2],
    })

    # 1. verify_scope
    scope_rep = await service.verify_scope("scope_math_g4", session=session)
    assert isinstance(scope_rep, ScopeStagingVerificationReport)
    assert len(scope_rep.layers) >= 1
    assert scope_rep.status in {StagingReadinessStatus.PARTIALLY_STAGEABLE, StagingReadinessStatus.BLOCKED_BY_COVERAGE}


    # 2. Scope not configured in registry
    scope_registry.get_scope_targets.side_effect = LookupError("not found")
    missing_scope_rep = await service.verify_scope("missing_scope", session=session)
    assert missing_scope_rep.status == StagingReadinessStatus.BLOCKED_BY_MISSING_SCOPE


    # 3. verify_all_scopes
    scope_registry.get_scope_targets.side_effect = None
    scope_registry.get_scope_targets.return_value = [target_mock]


    all_rep = await service.verify_all_scopes(session, actor_id="admin_user", persist=True)
    assert isinstance(all_rep, AllScopeStagingVerificationReport)
    assert len(all_rep.scopes) == 1

    # 4. list_runs & get_run_report
    run_rec = ContentStagingVerificationRun(
        run_id=uuid.uuid4(),
        status="completed",
        summary_json={"ready_scopes": 1},
        created_by="admin",
        created_at=datetime.now(timezone.utc),
    )
    scope_rec = ContentStagingVerificationScopeResult(
        run_id=run_rec.run_id,
        scope_id="scope_math_g4",
        status="ready_for_staging",
        can_seed_staging=True,
        can_promote_production=True,
        summary_json={"target": 2, "layers": []},
        blockers_json=[],
    )

    list_run_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[run_rec]))))
    session.execute.side_effect = None
    session.execute.return_value = list_run_res
    runs = await service.list_runs(session)
    assert len(runs) == 1

    session.get.return_value = run_rec
    scope_rows_res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[scope_rec]))))
    session.execute.return_value = scope_rows_res
    run_report = await service.get_run_report(session, run_rec.run_id)
    assert run_report.run_id == run_rec.run_id
    assert len(run_report.scopes) == 1

    # 4b. get_scope_blockers
    blockers = await service.get_scope_blockers("scope_math_g4", session=session)
    assert isinstance(blockers, list)


    # 4c. Staging verification run not found
    session.get.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.get_run_report(session, uuid.uuid4())

    # 4e. _layer_summary and _layer_blockers branches
    real_service = ContentStagingReadinessService(scope_registry=scope_registry)
    sum_ready = LayerReadinessSummary(

        layer="diagnostic_items",
        caps_ref="4.M.1.1",
        target=2,
        approved=2,
        stageable=2,
        invalid_provenance=1,
        invalid_license=1,
        low_source_quality=1,
        status=StagingReadinessStatus.READY_FOR_STAGING,
    )
    blockers_ready = real_service._layer_blockers(sum_ready)
    assert len(blockers_ready) == 3  # provenance, license, low quality

    sum_zero_target = LayerReadinessSummary(
        layer="diagnostic_items",
        caps_ref="4.M.1.1",
        target=0,
        status=StagingReadinessStatus.NOT_CONFIGURED,
    )
    b_zero = real_service._layer_blockers(sum_zero_target)
    assert b_zero[0].code == "target_not_configured"

    # Status calculation branches
    assert real_service._scope_status([sum_zero_target], []) == StagingReadinessStatus.NOT_CONFIGURED
    assert real_service._scope_status([sum_ready], []) == StagingReadinessStatus.READY_FOR_STAGING

    # 4f. Test _layer_summary with all artifact status conditions
    art_approved = ContentGenerationArtifact(artifact_id=uuid.uuid4(), status=ContentArtifactStatus.APPROVED, source_snapshot_hash="h1")
    src_clean = ContentArtifactSource(artifact_id=art_approved.artifact_id, source_hash="h1")
    s_ready = real_service._layer_summary("diagnostic_items", "4.M.1.1", 1, [art_approved], {art_approved.artifact_id: [src_clean]})
    assert s_ready.status == StagingReadinessStatus.READY_FOR_STAGING

    art_pending = ContentGenerationArtifact(artifact_id=uuid.uuid4(), status=ContentArtifactStatus.PENDING_REVIEW)
    s_rev = real_service._layer_summary("diagnostic_items", "4.M.1.1", 1, [art_pending], {})
    assert s_rev.status == StagingReadinessStatus.BLOCKED_BY_REVIEW

    art_gen = ContentGenerationArtifact(artifact_id=uuid.uuid4(), status=ContentArtifactStatus.GENERATED)
    art_val_fail = ContentGenerationArtifact(artifact_id=uuid.uuid4(), status=ContentArtifactStatus.VALIDATION_FAILED)
    s_val = real_service._layer_summary("diagnostic_items", "4.M.1.1", 1, [art_gen, art_val_fail], {})
    assert s_val.status == StagingReadinessStatus.BLOCKED_BY_VALIDATION

    # Unapproved provenance status
    art_no_prov = ContentGenerationArtifact(artifact_id=uuid.uuid4(), status=ContentArtifactStatus.APPROVED, source_snapshot_hash="h1")
    s_prov = real_service._layer_summary("diagnostic_items", "4.M.1.1", 1, [art_no_prov], {})
    assert s_prov.status == StagingReadinessStatus.BLOCKED_BY_PROVENANCE

    # Unmocked loaders
    session.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[art1]))))
    loaded = await real_service._load_scope_artifacts(session, "scope_math_g4")
    assert len(loaded) == 1
    src_idx = await real_service._load_source_index(session, [art1.artifact_id])
    assert len(src_idx) == 1



