"""Comprehensive unit tests covering staging preview, read verification, and seed promotion services."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.domain.content_coverage import ContentLayer, CoverageLayerStatus
from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentSeedRun,
    ContentStagingArtifact,
    ContentStagingSeedItem,
)
from app.services.content_seed_promotion import (
    ContentSeedPromotionService,
    GateResult,
)
from app.services.content_staging_preview_service import (
    ContentStagingPreviewService,
    StagingArtifactPreview,
    StagingCapsRefPreview,
    StagingPreviewReport,
)
from app.services.content_staging_read_verification import (
    ContentStagingReadVerificationService,
    ScopeStagingReadReport,
    StagingReadVerificationReport,
)


# ============================================================================
# ContentStagingPreviewService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_staging_preview_service():
    service = ContentStagingPreviewService()
    session = AsyncMock()

    art_id = uuid.uuid4()
    seed_id = uuid.uuid4()
    scope_id = "scope_math_g4"
    caps_ref = "4.M.1"

    gen_art = ContentGenerationArtifact(
        artifact_id=art_id,
        scope_id=scope_id,
        content_layer="diagnostic_items",
        status=ContentArtifactStatus.APPROVED,
    )
    staging_art_active = ContentStagingArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        scope_id=scope_id,
        caps_ref=caps_ref,
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={"q": 1},
        source_artifact_hash="hash123",
        staging_status="active",
        created_by_seed_run_id=seed_id,
        created_at=datetime.now(timezone.utc),
    )
    staging_art_pending = ContentStagingArtifact(
        id=uuid.uuid4(),
        artifact_id=uuid.uuid4(),
        scope_id=scope_id,
        caps_ref=caps_ref,
        layer="lessons",
        artifact_type="lesson",
        payload_json={"body": "abc"},
        source_artifact_hash="hash456",
        staging_status="pending",
        created_by_seed_run_id=None,
        created_at=datetime.now(timezone.utc),
    )

    # 1. preview_scope
    session.execute.return_value = [
        (staging_art_active, gen_art),
        (staging_art_pending, gen_art),
    ]
    session.scalar.side_effect = ["completed", "completed"]  # seed run status & verification status

    report = await service.preview_scope(session, scope_id, layers=["diagnostic_items", "lessons"])
    assert isinstance(report, StagingPreviewReport)
    assert report.total_artifacts_count == 2
    assert report.active_artifacts_count == 1
    assert report.pending_artifacts_count == 1
    assert report.learner_visible_count == 0
    assert len(report.artifacts) == 2
    assert report.artifacts[0].verification_passed is True

    # 2. preview_caps_ref
    session.execute.return_value = [
        (staging_art_active, gen_art),
    ]
    session.scalar.side_effect = [None, None]  # seed status None & verif status None

    caps_preview = await service.preview_caps_ref(session, scope_id, caps_ref, layers=["diagnostic_items"])
    assert isinstance(caps_preview, StagingCapsRefPreview)
    assert caps_preview.caps_ref == caps_ref
    assert caps_preview.total_artifacts_count == 1
    assert caps_preview.active_artifacts_count == 1
    assert caps_preview.learner_visible_count == 0

    # 3. _get_staging_verification_status branches
    session.scalar.side_effect = None
    session.scalar.return_value = "failed"
    assert await service._get_staging_verification_status(session, str(seed_id)) is False
    session.scalar.return_value = None
    assert await service._get_staging_verification_status(session, str(seed_id)) is None



# ============================================================================
# ContentStagingReadVerificationService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_staging_read_verification_service():
    service = ContentStagingReadVerificationService()
    session = AsyncMock()

    seed_id = uuid.uuid4()
    art_id = uuid.uuid4()
    scope_id = "scope_math_g4"

    # 1. verify_seed_run - missing staging row
    item_seeded = ContentStagingSeedItem(
        seed_run_id=seed_id,
        artifact_id=art_id,
        scope_id=scope_id,
        caps_ref="4.M.1",
        layer="diagnostic_items",
        status="seeded",
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item_seeded])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),  # no match
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),  # active rows count
    ]
    rep_missing = await service.verify_seed_run(session, seed_id)
    assert isinstance(rep_missing, StagingReadVerificationReport)
    assert rep_missing.passed is False
    assert "Missing staging record" in rep_missing.errors[0]

    # 2. verify_seed_run - multiple staging rows, inactive, mismatched scope/caps/layer, deleted source, invalid status
    staging_art_bad = ContentStagingArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        scope_id="mismatched_scope",
        caps_ref="mismatched_caps",
        layer="mismatched_layer",
        staging_status="pending",
        created_by_seed_run_id=seed_id,
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item_seeded])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art_bad, staging_art_bad])))),  # multiple
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),  # count mismatch
    ]
    session.get.return_value = None  # source artifact deleted
    rep_bad = await service.verify_seed_run(session, seed_id)
    assert rep_bad.passed is False
    assert any("Multiple staging records" in err for err in rep_bad.errors)
    assert any("not active" in err for err in rep_bad.errors)
    assert any("mismatched scope" in err for err in rep_bad.errors)
    assert any("mismatched caps_ref" in err for err in rep_bad.errors)
    assert any("mismatched layer" in err for err in rep_bad.errors)
    assert any("deleted" in err for err in rep_bad.errors)

    # 3. verify_seed_run - source invalid status
    src_pending = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.PENDING_REVIEW,
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item_seeded])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art_bad])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art_bad])))),
    ]
    session.get.return_value = src_pending
    rep_invalid_src = await service.verify_seed_run(session, seed_id)
    assert any("status invalid for staging" in err for err in rep_invalid_src.errors)

    # 4. verify_seed_run - clean pass
    staging_art_ok = ContentStagingArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        scope_id=scope_id,
        caps_ref="4.M.1",
        layer="diagnostic_items",
        staging_status="active",
        created_by_seed_run_id=seed_id,
    )
    src_approved = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.APPROVED,
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item_seeded])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art_ok])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art_ok])))),
    ]
    session.get.return_value = src_approved
    rep_ok = await service.verify_seed_run(session, seed_id)
    assert rep_ok.passed is True
    assert rep_ok.verified_count == 1
    assert len(rep_ok.errors) == 0

    # 5. verify_scope_staging
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art_ok])))),
    ]
    session.get.return_value = src_approved
    scope_rep_ok = await service.verify_scope_staging(session, scope_id, layers=["diagnostic_items"])
    assert isinstance(scope_rep_ok, ScopeStagingReadReport)
    assert scope_rep_ok.passed is True
    assert scope_rep_ok.staged_artifacts_count == 1

    # verify_scope_staging with missing and rejected source
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art_ok, staging_art_ok])))),
    ]
    src_rej = ContentGenerationArtifact(artifact_id=art_id, status=ContentArtifactStatus.REJECTED)
    session.get.side_effect = [None, src_rej]
    scope_rep_bad = await service.verify_scope_staging(session, scope_id)
    assert scope_rep_bad.passed is False
    assert any("source missing" in err for err in scope_rep_bad.errors)
    assert any("status is rejected" in err for err in scope_rep_bad.errors)


# ============================================================================
# ContentSeedPromotionService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_seed_promotion_service():
    coverage_service = AsyncMock()
    verification_service = AsyncMock()
    seed_executor = AsyncMock()
    production_gate = AsyncMock()

    service = ContentSeedPromotionService(
        coverage_service=coverage_service,
        verification_service=verification_service,
        seed_executor=seed_executor,
        production_gate=production_gate,
    )
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    scope_id = "scope_math_g4"

    # Setup coverage response helper
    mock_item_green = MagicMock(approved=10, status=CoverageLayerStatus.GREEN)
    mock_caps_cov = MagicMock(
        caps_ref="4.M.1",
        layers={ContentLayer.DIAGNOSTIC_ITEMS: mock_item_green},
    )
    coverage_service.get_scope_coverage.return_value = MagicMock(per_caps_ref=[mock_caps_cov])

    # 1. dry_run_seed - passed
    run_dry = await service.dry_run_seed(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert isinstance(run_dry, ContentSeedRun)
    assert run_dry.status == "passed"
    assert run_dry.dry_run is True

    # 2. dry_run_seed - red coverage partial
    mock_item_red = MagicMock(approved=5, status=CoverageLayerStatus.RED)
    mock_caps_cov_red = MagicMock(
        caps_ref="4.M.1",
        layers={ContentLayer.DIAGNOSTIC_ITEMS: mock_item_red},
    )
    coverage_service.get_scope_coverage.return_value = MagicMock(per_caps_ref=[mock_caps_cov_red])
    run_dry_partial = await service.dry_run_seed(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert run_dry_partial.status == "partial"

    # 3. seed_staging - gate failed with allow_partial=False
    with pytest.raises(ValueError, match="Staging seed gate failed"):
        await service.seed_staging(session, scope_id, actor_id="admin", layers=[ContentLayer.DIAGNOSTIC_ITEMS], allow_partial=False)

    # 4. seed_staging - success with allow_partial=True
    seed_id = uuid.uuid4()
    seed_executor.seed_staging.return_value = MagicMock(
        seed_run_id=seed_id,
        status="seeded_staging",
        seeded_count=5,
        skipped_count=0,
        errors=[],
    )
    session.get.return_value = None  # creates new ContentSeedRun in DB
    run_seeded = await service.seed_staging(session, scope_id, actor_id="admin", layers=[ContentLayer.DIAGNOSTIC_ITEMS], allow_partial=True)
    assert isinstance(run_seeded, ContentSeedRun)
    assert run_seeded.status == "seeded_staging"
    assert run_seeded.summary["actor_id"] == "admin"

    # 5. verify_staging_seed
    verification_service.verify_scope_staging.return_value = MagicMock(
        passed=False,
        errors=["read check failed"],
        staged_artifacts_count=0,
    )
    gate_res_fail = await service.verify_staging_seed(session, scope_id)
    assert isinstance(gate_res_fail, GateResult)
    assert gate_res_fail.passed is False

    verification_service.verify_scope_staging.return_value = MagicMock(
        passed=True,
        errors=[],
        staged_artifacts_count=5,
    )
    gate_res_ok = await service.verify_staging_seed(session, scope_id)
    assert gate_res_ok.passed is True

    # 6. promote_production - gate failed
    production_gate.evaluate_scope.return_value = MagicMock(
        status=MagicMock(value="blocked_by_coverage"),
        blockers=[MagicMock(message="Coverage is red")],
    )
    with pytest.raises(ValueError, match="Production promotion gate failed: blocked_by_coverage"):
        await service.promote_production(session, scope_id, actor_id="admin")

    # 7. promote_production - staging verification failed
    production_gate.evaluate_scope.return_value = MagicMock(
        status=MagicMock(value="promotable"),
        blockers=[],
        coverage_summary={"cov": "ok"},
        staging_summary={"stage": "ok"},
    )
    verification_service.verify_scope_staging.return_value = MagicMock(
        passed=False,
        errors=["staging read broken"],
        staged_artifacts_count=0,
    )
    with pytest.raises(ValueError, match="Staging verification failed"):
        await service.promote_production(session, scope_id, actor_id="admin")

    # 8. promote_production - clean success
    verification_service.verify_scope_staging.return_value = MagicMock(
        passed=True,
        errors=[],
        staged_artifacts_count=10,
    )
    res_prom = await service.promote_production(session, scope_id, actor_id="admin")
    assert res_prom.passed is True
    assert res_prom.summary == {"cov": "ok", "stage": "ok"}
