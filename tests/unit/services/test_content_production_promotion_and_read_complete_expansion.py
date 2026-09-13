"""Comprehensive unit tests covering production promotion executor, gate, and read verification services."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.domain.content_coverage import ContentLayer, CoverageLayerStatus
from app.models.content_factory import (
    ContentArtifactReview,
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentProductionArtifact,
    ContentPromotionEvent,
    ContentReviewAction,
    ContentStagingArtifact,
    ContentStagingSeedItem,
    ContentValidationReport,
)
from app.services.content_production_promotion_executor import (
    ContentProductionPromotionExecutor,
    ProductionPromotionPage,
    ProductionPromotionPlan,
    ProductionPromotionResult,
    ProductionRollbackResult,
)
from app.services.content_production_promotion_gate import (
    ContentProductionPromotionGate,
    ProductionGateBlocker,
    ProductionGateReport,
    ProductionGateStatus,
)
from app.services.content_production_read_verification import (
    ContentProductionReadVerificationService,
    ProductionReadVerificationReport,
    ScopeProductionReadReport,
)
from sqlalchemy import Column, DateTime, JSON, String, Uuid
from app.core.database import Base


@pytest.fixture(autouse=True)
def mock_content_promotion_event(monkeypatch):
    class MockContentPromotionEvent(Base):
        __tablename__ = "test_mock_complete_content_promotion_events"
        __table_args__ = {"extend_existing": True}

        event_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
        scope_id = Column(String, nullable=True)
        promoted_by = Column(String, nullable=True)
        status = Column(String, nullable=True)
        summary = Column(JSON, default=dict)
        created_at = Column(DateTime, nullable=True)
        updated_at = Column(DateTime, nullable=True)

    monkeypatch.setattr(
        "app.services.content_production_promotion_executor.ContentPromotionEvent",
        MockContentPromotionEvent,
    )
    return MockContentPromotionEvent



# ============================================================================
# ContentProductionReadVerificationService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_production_read_verification_service():
    service = ContentProductionReadVerificationService()
    session = AsyncMock()

    event_id = uuid.uuid4()
    art_id = uuid.uuid4()

    # 1. verify_promotion_event - event not found
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    rep_not_found = await service.verify_promotion_event(session, event_id)
    assert isinstance(rep_not_found, ProductionReadVerificationReport)
    assert rep_not_found.passed is False
    assert "not found" in rep_not_found.errors[0]

    # 2. verify_promotion_event - non-active production status
    mock_event = MagicMock(spec=ContentPromotionEvent, promotion_event_id=event_id)
    prod_art_inactive = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        scope_id="scope_math",
        caps_ref="4.M.1",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={"q": 1},
        production_status="superseded",
        created_by_promotion_event_id=event_id,
    )

    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_event)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[prod_art_inactive])))),
    ]
    rep_inactive = await service.verify_promotion_event(session, event_id)
    assert rep_inactive.passed is False
    assert "not active" in rep_inactive.errors[0]

    # 3. verify_promotion_event - source artifact missing
    prod_art_active = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        production_status="active",
        created_by_promotion_event_id=event_id,
    )
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_event)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[prod_art_active])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # source artifact missing
    ]
    rep_missing_src = await service.verify_promotion_event(session, event_id)
    assert rep_missing_src.passed is False
    assert "Source artifact" in rep_missing_src.errors[0]

    # 4. verify_promotion_event - source artifact not approved
    src_art_pending = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.PENDING_REVIEW,
    )
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_event)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[prod_art_active])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=src_art_pending)),
    ]
    rep_not_approved = await service.verify_promotion_event(session, event_id)
    assert rep_not_approved.passed is False
    assert "points to non-approved artifact" in rep_not_approved.errors[0]

    # 5. verify_promotion_event - all pass
    src_art_approved = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.APPROVED,
    )
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_event)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[prod_art_active])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=src_art_approved)),
    ]
    rep_ok = await service.verify_promotion_event(session, event_id)
    assert rep_ok.passed is True
    assert rep_ok.verified_count == 1
    assert len(rep_ok.errors) == 0

    # 6. verify_scope_production - all paths
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[prod_art_active])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=src_art_approved)),
    ]
    scope_rep = await service.verify_scope_production(session, "scope_math")
    assert isinstance(scope_rep, ScopeProductionReadReport)
    assert scope_rep.passed is True
    assert scope_rep.production_artifacts_count == 1

    # verify_scope_production with missing source and not approved
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[prod_art_active, prod_art_active])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=src_art_pending)),
    ]
    scope_rep_bad = await service.verify_scope_production(session, "scope_math")
    assert scope_rep_bad.passed is False
    assert len(scope_rep_bad.errors) == 2


# ============================================================================
# ContentProductionPromotionGate Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_production_promotion_gate():
    coverage_service = AsyncMock()
    gate = ContentProductionPromotionGate(coverage_service=coverage_service)
    session = AsyncMock()

    art_id = uuid.uuid4()
    scope_id = "scope_math_g4"

    # 1. evaluate_scope - blocked by coverage
    mock_cov_red = MagicMock(
        status=CoverageLayerStatus.RED,
        coverage_percentage=50.0,
        target_percentage=100.0,
    )
    coverage_service.get_coverage.return_value = mock_cov_red

    # staging seed query returns empty
    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    )

    report_cov = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert isinstance(report_cov, ProductionGateReport)
    assert report_cov.status == ProductionGateStatus.BLOCKED_BY_COVERAGE

    with pytest.raises(ValueError, match="Production promotion gate failed for scope"):
        await gate.assert_promotable(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])

    # 2. evaluate_scope - blocked by staging missing / status
    mock_cov_green = MagicMock(
        status=CoverageLayerStatus.GREEN,
        coverage_percentage=100.0,
        target_percentage=100.0,
    )
    coverage_service.get_coverage.return_value = mock_cov_green

    # Seeded item exists, but staging artifact missing or inactive
    seed_item = ContentStagingSeedItem(artifact_id=art_id, scope_id=scope_id, status="seeded")
    staging_art_inactive = ContentStagingArtifact(
        artifact_id=art_id,
        scope_id=scope_id,
        staging_status="pending",
    )

    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[seed_item])))),  # seeded items
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # staging artifact missing
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),  # generation artifacts
    ]
    report_stage_missing = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert report_stage_missing.status == ProductionGateStatus.BLOCKED_BY_STAGING

    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[seed_item])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=staging_art_inactive)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]
    report_stage_inactive = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert report_stage_inactive.status == ProductionGateStatus.BLOCKED_BY_STAGING

    # 3. evaluate_scope - artifact status & review & provenance & validation blockers
    staging_art_active = ContentStagingArtifact(
        artifact_id=art_id,
        scope_id=scope_id,
        staging_status="active",
    )

    # Artifact not approved -> BLOCKED_BY_REVIEW
    gen_art_pending = ContentGenerationArtifact(
        artifact_id=art_id,
        scope_id=scope_id,
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        status=ContentArtifactStatus.PENDING_REVIEW,
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[seed_item])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=staging_art_active)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[gen_art_pending])))),
    ]
    report_review = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert report_review.status == ProductionGateStatus.BLOCKED_BY_REVIEW

    # Artifact approved, but no source -> BLOCKED_BY_PROVENANCE
    gen_art_approved = ContentGenerationArtifact(
        artifact_id=art_id,
        scope_id=scope_id,
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        status=ContentArtifactStatus.APPROVED,
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[seed_item])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=staging_art_active)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[gen_art_approved])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),  # no sources
    ]
    report_prov = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert report_prov.status == ProductionGateStatus.BLOCKED_BY_PROVENANCE

    # Artifact approved, has source, but no approval review record -> BLOCKED_BY_REVIEW
    mock_src = ContentArtifactSource(artifact_id=art_id)
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[seed_item])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=staging_art_active)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[gen_art_approved])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_src)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),  # no review
    ]
    report_rev_rec = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert report_rev_rec.status == ProductionGateStatus.BLOCKED_BY_REVIEW

    # Artifact approved, has review, but no validation report / failed validation report -> BLOCKED_BY_VALIDATION
    mock_review = ContentArtifactReview(artifact_id=art_id, review_action=ContentReviewAction.APPROVE)
    val_fail = ContentValidationReport(artifact_id=art_id, passed=False)

    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[seed_item])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=staging_art_active)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[gen_art_approved])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_src)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_review)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=val_fail)),
    ]
    report_val = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert report_val.status == ProductionGateStatus.BLOCKED_BY_VALIDATION

    # 4. evaluate_scope - clean PROMOTABLE
    val_pass = ContentValidationReport(artifact_id=art_id, passed=True)
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[seed_item])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=staging_art_active)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[gen_art_approved])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_src)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_review)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=val_pass)),
    ]
    report_ok = await gate.evaluate_scope(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])
    assert report_ok.status == ProductionGateStatus.PROMOTABLE
    assert len(report_ok.blockers) == 0

    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[seed_item])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=staging_art_active)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[gen_art_approved])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_src)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_review)))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=val_pass)),
    ]
    await gate.assert_promotable(session, scope_id, layers=[ContentLayer.DIAGNOSTIC_ITEMS])


# ============================================================================
# ContentProductionPromotionExecutor Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_production_promotion_executor():
    gate = AsyncMock()
    executor = ContentProductionPromotionExecutor(gate=gate)
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    scope_id = "scope_math_g4"

    # 1. dry_run_promotion - gate failure
    gate.evaluate_scope.return_value = MagicMock(
        status=MagicMock(value="blocked_by_coverage"),
        blockers=[MagicMock(message="Coverage is low")],
    )
    with pytest.raises(ValueError, match="Cannot dry-run promotion"):
        await executor.dry_run_promotion(session, scope_id, actor_id="admin")

    # 2. dry_run_promotion - success
    gate.evaluate_scope.return_value = MagicMock(status=MagicMock(value="promotable"))
    staging_art = ContentStagingArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        scope_id=scope_id,
        caps_ref="4.M.1",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={"q": 1},
        source_artifact_hash="hash123",
        staging_status="active",
    )
    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art])))
    )

    plan = await executor.dry_run_promotion(session, scope_id, actor_id="admin")
    assert isinstance(plan, ProductionPromotionPlan)
    assert plan.promotable_count == 1
    assert plan.skipped_count == 0

    # 3. promote_scope - confirmation mismatch
    with pytest.raises(ValueError, match="Confirmation mismatch"):
        await executor.promote_scope(session, scope_id, actor_id="admin", confirmation="WRONG CONFIRMATION")

    # 4. promote_scope - gate failure
    gate.evaluate_scope.return_value = MagicMock(
        status=MagicMock(value="blocked_by_staging"),
        blockers=[MagicMock(message="Staging blocked")],
    )
    with pytest.raises(ValueError, match="Cannot promote: gate status is"):
        await executor.promote_scope(
            session,
            scope_id,
            actor_id="admin",
            confirmation=f"PROMOTE {scope_id} TO PRODUCTION",
        )

    # 5. promote_scope - success (with existing active production artifact to supersede)
    gate.evaluate_scope.return_value = MagicMock(
        status=MagicMock(value="promotable"),
        coverage_summary={"cov": "ok"},
        staging_summary={"stage": "ok"},
    )
    existing_prod = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        production_status="active",
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[staging_art])))),
        MagicMock(scalar_one_or_none=MagicMock(return_value=existing_prod)),  # existing found
    ]

    res_promote = await executor.promote_scope(
        session,
        scope_id,
        actor_id="admin",
        confirmation=f"PROMOTE {scope_id} TO PRODUCTION",
    )
    assert isinstance(res_promote, ProductionPromotionResult)
    assert res_promote.status == "succeeded"
    assert res_promote.promoted_count == 1
    assert existing_prod.production_status == "superseded"
    session.add.assert_called()

    # 6. get_promotion_event
    event_id = uuid.uuid4()
    mock_event = MagicMock(
        event_id=event_id,
        scope_id=scope_id,
        status="succeeded",
        summary={"promoted_count": 1},
    )
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # not found
    ]
    with pytest.raises(ValueError, match="not found"):
        await executor.get_promotion_event(session, event_id)


    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_event)),
        MagicMock(scalar=MagicMock(return_value=1)),  # count
    ]
    got_event = await executor.get_promotion_event(session, event_id)
    assert got_event.promotion_event_id == event_id
    assert got_event.promoted_count == 1

    # 7. list_promotion_events
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_event])))),
        MagicMock(scalar=MagicMock(return_value=1)),  # total count
        MagicMock(scalar=MagicMock(return_value=1)),  # event count
    ]
    page = await executor.list_promotion_events(session, scope_id=scope_id, limit=10, offset=0)
    assert isinstance(page, ProductionPromotionPage)
    assert page.total == 1
    assert len(page.items) == 1

    # 8. rollback_promotion
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),  # event not found
    ]
    with pytest.raises(ValueError, match="not found"):
        await executor.rollback_promotion(session, event_id, actor_id="admin", reason="bug detected")

    active_prod = ContentProductionArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        production_status="active",
    )
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_event)),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[active_prod])))),
    ]
    res_rb = await executor.rollback_promotion(session, event_id, actor_id="admin", reason="bug detected")
    assert isinstance(res_rb, ProductionRollbackResult)
    assert res_rb.status == "rolled_back"
    assert res_rb.rolled_back_count == 1
    assert active_prod.production_status == "rolled_back"
    assert mock_event.status == "rolled_back"
