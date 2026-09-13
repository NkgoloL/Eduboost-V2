"""Comprehensive unit tests covering content coverage service and content staging readiness service."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.domain.content_coverage import (
    CapsRefCoverageReport,
    ContentLayer,
    CoverageLayerCounts,
    CoverageLayerStatus,
    ScopeCoverageLayerSummary,
    ScopeCoverageReport,
    ScopeCoverageSummary,
)
from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentStagingVerificationRun,
    ContentStagingVerificationScopeResult,
)
from app.services.content_coverage_service import (
    ContentCoverageService,
    CoverageGateLayerReport,
    _status,
    build_content_coverage_service,
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


# ============================================================================
# ContentCoverageService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_coverage_service():
    registry = MagicMock()
    item_repo = AsyncMock()
    lesson_repo = AsyncMock()

    service = ContentCoverageService(
        scope_registry=registry,
        item_repo=item_repo,
        lesson_repo=lesson_repo,
    )

    scope_id = "scope_math_g4"
    caps_ref = "4.M.1"

    mock_scope = MagicMock(
        scope_id=scope_id,
        grade=4,
        subject_code="MATH",
        language="en",
        caps_refs=[caps_ref],
    )
    registry.get_scope.return_value = mock_scope
    registry.get_scope_caps_refs.return_value = [caps_ref]
    registry.get_coverage_target.return_value = 5

    # 1. get_caps_ref_coverage - outside scope lookup error
    with pytest.raises(LookupError, match="outside content scope"):
        await service.get_caps_ref_coverage(scope_id, "9.9.9")

    # 2. _diagnostic_counts and _lesson_counts mocks
    item_repo.get_coverage_summary.return_value = {
        caps_ref: {
            "approved": 5,
            "ai_generated": 2,
            "human_reviewed": 1,
            "rejected": 0,
        }
    }
    lesson_1 = MagicMock(review_status="approved")
    lesson_2 = MagicMock(review_status="ai_generated")
    lesson_3 = MagicMock(review_status="rejected")
    lesson_repo.list_by_caps_ref.return_value = [lesson_1, lesson_2, lesson_3]

    # 3. get_scope_coverage
    rep = await service.get_scope_coverage(scope_id)
    assert isinstance(rep, ScopeCoverageReport)
    assert rep.scope_id == scope_id
    assert rep.summary.total_caps_refs == 1
    assert rep.summary.red_refs == 1


    # 4. get_coverage gate layer report (diagnostic layer)
    res_gate = await service.get_coverage(None, scope_id, ContentLayer.DIAGNOSTIC_ITEMS)
    assert isinstance(res_gate, CoverageGateLayerReport)
    assert res_gate.status == CoverageLayerStatus.GREEN
    assert res_gate.approved_total == 5

    # 5. get_coverage gate layer report (blueprints artifact layer DB check)
    session = AsyncMock()
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=4))
    res_bp = await service.get_coverage(session, scope_id, ContentLayer.ASSESSMENT_BLUEPRINTS)
    assert res_bp.approved_total == 4

    # 6. Target lookup error fallback in _layer_counts
    registry.get_coverage_target.side_effect = LookupError("target not configured")
    counts = await service._layer_counts(scope_id, caps_ref, ContentLayer.STUDY_PLAN_TEMPLATES)
    assert counts.target == 0

    # 7. None repos fallbacks
    empty_service = ContentCoverageService(scope_registry=registry, item_repo=None, lesson_repo=None)
    assert (await empty_service._diagnostic_counts(caps_ref))["approved"] == 0
    assert (await empty_service._lesson_counts(caps_ref))["approved"] == 0

    # 8. builder and helper functions
    built = build_content_coverage_service(item_repo, lesson_repo)
    assert isinstance(built, ContentCoverageService)
    assert _status(lesson_1) == "approved"
    assert _status(MagicMock(review_status=MagicMock(value="custom_status"))) == "custom_status"

    from_sess = ContentCoverageService.from_session(AsyncMock())
    assert from_sess is not None


# ============================================================================
# ContentStagingReadinessService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_staging_readiness_service():
    registry = MagicMock()
    service = ContentStagingReadinessService(scope_registry=registry)
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    scope_id = "scope_math_g4"
    caps_ref = "4.M.1"
    art_id = uuid.uuid4()

    # 1. Missing scope lookup error
    registry.get_scope_targets.side_effect = LookupError("Missing scope")
    rep_missing = await service.verify_scope(scope_id, session=session)
    assert rep_missing.status == StagingReadinessStatus.BLOCKED_BY_MISSING_SCOPE
    assert rep_missing.can_seed_staging is False

    # 2. Configured scope with various layer states
    mock_target = MagicMock(
        caps_ref=caps_ref,
        targets={"diagnostic_items.target": 5, "lessons.target": 0},
    )
    registry.get_scope_targets.side_effect = None
    registry.get_scope_targets.return_value = [mock_target]

    # Artifacts for this scope
    art_approved = ContentGenerationArtifact(
        artifact_id=art_id,
        scope_id=scope_id,
        caps_ref=caps_ref,
        content_layer="diagnostic_items",
        status=ContentArtifactStatus.APPROVED,
        source_snapshot_hash="snap1",
    )
    session.execute.side_effect = [
        # _load_scope_artifacts
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[art_approved])))),
        # _load_source_index
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[
            ContentArtifactSource(
                source_id=uuid.uuid4(),
                artifact_id=art_id,
                source_hash="shash1",
                license_status="active",
                source_quality_score=0.9,
            )
        ])))),
    ]

    rep_part = await service.verify_scope(scope_id, session=session, include_partial=True)
    assert isinstance(rep_part, ScopeStagingVerificationReport)
    assert rep_part.can_seed_staging is True  # 1 stageable item out of 5 required -> partially stageable
    assert rep_part.status == StagingReadinessStatus.PARTIALLY_STAGEABLE

    # 3. get_scope_blockers
    registry.get_scope_targets.return_value = [mock_target]
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[art_approved])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]
    blockers = await service.get_scope_blockers(scope_id, session=session)
    assert len(blockers) > 0

    # 4. verify_all_scopes and persist_report
    mock_scope_obj = MagicMock(scope_id=scope_id)
    registry.list_active_scopes.return_value = [mock_scope_obj]
    registry.list_scopes.return_value = [mock_scope_obj]

    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[art_approved])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]
    all_report = await service.verify_all_scopes(
        session,
        actor_id="admin",
        persist=True,
        include_review_scopes=False,
    )
    assert isinstance(all_report, AllScopeStagingVerificationReport)
    assert all_report.status == "completed"
    assert all_report.run_id is not None
    session.add.assert_called()

    # 5. list_runs and get_run_report
    run_uuid = uuid.uuid4()
    mock_run = ContentStagingVerificationRun(
        run_id=run_uuid,
        status="completed",
        summary_json={"ready_scopes": 1},
        created_by="admin",
        created_at=datetime.now(timezone.utc),
    )
    mock_scope_res = ContentStagingVerificationScopeResult(
        run_id=run_uuid,
        scope_id=scope_id,
        status="ready_for_staging",
        can_seed_staging=True,
        can_promote_production=True,
        summary_json={"layers": []},
        blockers_json=[],
    )

    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_run])))),
    ]
    runs = await service.list_runs(session)
    assert len(runs) == 1

    session.get.return_value = None
    with pytest.raises(LookupError, match="Staging verification run .* not found"):
        await service.get_run_report(session, run_uuid)

    session.get.return_value = mock_run
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_scope_res])))),
    ]
    got_rep = await service.get_run_report(session, run_uuid)
    assert got_rep.run_id == run_uuid
    assert len(got_rep.scopes) == 1

    # 6. Empty targets case and blockers
    registry.get_scope_targets.return_value = []
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]
    rep_empty = await service.verify_scope(scope_id, session=session)
    assert any(b.code == "missing_targets" for b in rep_empty.blockers)

    # 7. Layer blockers with invalid license & low quality sources
    mock_target_single = MagicMock(caps_ref=caps_ref, targets={"diagnostic_items.target": 5})
    registry.get_scope_targets.return_value = [mock_target_single]
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[art_approved])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[
            ContentArtifactSource(
                source_id=uuid.uuid4(),
                artifact_id=art_id,
                source_hash="shash1",
                license_status="rejected",
                source_quality_score=0.2,
            )
        ])))),
    ]
    rep_bad_source = await service.verify_scope(scope_id, session=session)
    assert any(b.code == "invalid_license" for b in rep_bad_source.blockers)
    assert any(b.code == "low_source_quality" for b in rep_bad_source.blockers)


    # 6. Edge provenance helpers
    assert service._has_valid_provenance(ContentGenerationArtifact(source_snapshot_hash=None), [MagicMock()]) is False
    assert service._has_valid_provenance(ContentGenerationArtifact(source_snapshot_hash="h1"), []) is False
    assert service._has_invalid_license([MagicMock(license_status="restricted")]) is True
    assert service._has_invalid_license([MagicMock(license_status="commercial")]) is False
    assert service._has_low_source_quality([MagicMock(source_quality_score=0.3)]) is True
    assert service._has_low_source_quality([MagicMock(source_quality_score=0.8)]) is False

    assert _value(StagingReadinessStatus.READY_FOR_STAGING) == "ready_for_staging"
