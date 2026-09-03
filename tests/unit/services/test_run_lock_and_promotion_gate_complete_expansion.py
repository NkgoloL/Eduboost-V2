from unittest.mock import AsyncMock, MagicMock
import time
import uuid
import pytest

from app.domain.content_coverage import ContentLayer, CoverageLayerStatus
from app.models.content_factory import (
    ContentArtifactReview,
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAction,
    ContentStagingArtifact,
    ContentStagingSeedItem,
    ContentValidationReport,
)
from app.services.content_generation_run_lock import (
    ContentGenerationRunLock,
    LockAcquisitionResult,
)
from app.services.content_production_promotion_gate import (
    ContentProductionPromotionGate,
    ProductionGateStatus,
)


@pytest.mark.asyncio
async def test_content_generation_run_lock_lifecycle():
    lock = ContentGenerationRunLock(ttl_minutes=60)
    session = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    # Case 1: No existing run -> placeholder created and acquired
    scalar_mock = MagicMock()
    scalar_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = scalar_mock

    res = await lock.acquire(session, holder="test_worker_1")
    assert isinstance(res, LockAcquisitionResult)
    assert res.acquired is True
    assert res.lock_holder == "test_worker_1"
    assert session.add.called
    assert session.flush.called

    # Case 2b: Stale lock -> released and acquired on existing run
    stale_run = MagicMock()
    stale_run.run_metadata = {
        "full_generation_lock": {
            "holder": "dead_worker",
            "lock_acquired_at": time.time() - 10000,
            "lock_expires_at": time.time() - 5000,
        }
    }
    scalar_mock.scalar_one_or_none.return_value = stale_run
    stale_acquired = await lock.acquire(session, holder="new_worker")
    assert stale_acquired.acquired is True
    assert stale_acquired.lock_holder == "new_worker"

    # Case 3: Active unexpired lock exists -> acquisition denied
    stale_run.run_metadata = {
        "full_generation_lock": {
            "holder": "other_worker",
            "lock_acquired_at": time.time(),
            "lock_expires_at": time.time() + 3600,
        }
    }
    denied = await lock.acquire(session, holder="test_worker_2")
    assert denied.acquired is False
    assert denied.error == "Lock already held"

    # Case 4: Release lock
    released = await lock.release(session, holder="other_worker")
    assert released is True

    # Case 5: Release with wrong holder -> False
    denied_release = await lock.release(session, holder="wrong_holder")
    assert denied_release is False


@pytest.mark.asyncio
async def test_content_production_promotion_gate_evaluations():
    mock_coverage_service = AsyncMock()
    gate = ContentProductionPromotionGate(coverage_service=mock_coverage_service)
    session = AsyncMock()
    session.execute = AsyncMock()

    scope_id = "test_scope_math_g4"

    # 1. Coverage blocker test
    coverage_result = MagicMock()
    coverage_result.status = CoverageLayerStatus.RED
    coverage_result.coverage_percentage = 20.0
    coverage_result.target_percentage = 100.0
    mock_coverage_service.get_coverage.return_value = coverage_result

    empty_result = MagicMock()
    empty_result.scalars.return_value.all.return_value = []
    empty_result.scalar_one_or_none.return_value = None
    session.execute.return_value = empty_result

    report = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert report.status == ProductionGateStatus.BLOCKED_BY_COVERAGE
    assert any("Coverage for layer" in b.message for b in report.blockers)

    with pytest.raises(ValueError, match="Production promotion gate failed"):
        await gate.assert_promotable(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])

    # 2. Coverage GREEN, but Staging items present and active
    coverage_result.status = CoverageLayerStatus.GREEN
    mock_coverage_service.get_coverage.return_value = coverage_result

    seed_item = MagicMock()
    seed_item.artifact_id = uuid.uuid4()
    seed_item.caps_ref = "4.M.1.1"

    staging_art = MagicMock()
    staging_art.staging_status = "active"

    # Successful staging verification query mocks
    staging_seeds = MagicMock()
    staging_seeds.scalars.return_value.all.return_value = [seed_item]

    staging_query = MagicMock()
    staging_query.scalar_one_or_none.return_value = staging_art

    # Valid artifact with complete provenance, review and validation
    valid_art = MagicMock()
    valid_art.artifact_id = seed_item.artifact_id
    valid_art.caps_ref = "4.M.1.1"
    valid_art.status = ContentArtifactStatus.APPROVED

    artifacts_query = MagicMock()
    artifacts_query.scalars.return_value.all.return_value = [valid_art]

    provenance_query = MagicMock()
    provenance_query.scalars.return_value.first.return_value = MagicMock()

    review_query = MagicMock()
    review_query.scalars.return_value.first.return_value = MagicMock()

    val_rep = MagicMock()
    val_rep.passed = True
    val_query = MagicMock()
    val_query.scalar_one_or_none.return_value = val_rep

    session.execute.side_effect = [
        staging_seeds,
        staging_query,
        artifacts_query,
        provenance_query,
        review_query,
        val_query,
    ]

    clean_report = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert clean_report.status == ProductionGateStatus.PROMOTABLE
    assert len(clean_report.blockers) == 0

    # Promotable assert passes cleanly
    session.execute.side_effect = [
        staging_seeds,
        staging_query,
        artifacts_query,
        provenance_query,
        review_query,
        val_query,
    ]
    await gate.assert_promotable(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])

    # 3. Blocker branches: Artifact not approved
    unapproved_art = MagicMock()
    unapproved_art.status = ContentArtifactStatus.DRAFT
    unapproved_art.artifact_id = uuid.uuid4()
    unapproved_art.caps_ref = "4.M.1.1"

    session.execute.side_effect = [
        staging_seeds,
        staging_query,
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[unapproved_art])))),
    ]
    rep_unapproved = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert rep_unapproved.status == ProductionGateStatus.BLOCKED_BY_REVIEW

    # 4. Blocker branches: Missing provenance
    session.execute.side_effect = [
        staging_seeds,
        staging_query,
        artifacts_query,
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
    ]
    rep_noprov = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert rep_noprov.status == ProductionGateStatus.BLOCKED_BY_PROVENANCE

    # 4b. Blocker branches: Missing review approval
    session.execute.side_effect = [
        staging_seeds,
        staging_query,
        artifacts_query,
        provenance_query,
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
    ]
    rep_norev = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert rep_norev.status == ProductionGateStatus.BLOCKED_BY_REVIEW

    # 5. Blocker branches: Validation failure

    bad_val = MagicMock(passed=False)
    session.execute.side_effect = [
        staging_seeds,
        staging_query,
        artifacts_query,
        provenance_query,
        review_query,
        MagicMock(scalar_one_or_none=MagicMock(return_value=bad_val)),
    ]
    rep_badval = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert rep_badval.status == ProductionGateStatus.BLOCKED_BY_VALIDATION



