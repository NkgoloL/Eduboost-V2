"""Comprehensive unit tests covering content artifact lifecycle, bulk review, and review risk scoring services."""
import os
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
)
from app.services.content_artifact_lifecycle import (
    ArtifactStatusTransition,
    ContentArtifactLifecycleService,
    _value,
)
from app.services.content_bulk_review import BulkReviewResult, ContentBulkReviewService
from app.services.content_review_risk import ContentReviewRiskService, ReviewRisk


# ============================================================================
# ContentArtifactLifecycleService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_artifact_lifecycle_service():
    factory_service = AsyncMock()
    governance_service = AsyncMock()
    service = ContentArtifactLifecycleService(
        factory_service=factory_service,
        governance_service=governance_service,
    )
    session = AsyncMock()
    session.flush = AsyncMock()

    art_id = uuid.uuid4()
    art = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.GENERATED,
        publication_eligible=False,
    )
    factory_service.get_artifact.return_value = art

    # 1. create_artifact
    factory_service.create_artifact.return_value = art
    created = await service.create_artifact(session, payload={"title": "test"})
    assert created == art

    # 2. validate_for_review
    factory_service.validate_existing_artifact.return_value = MagicMock(passed=True, errors=[])
    v_rep = await service.validate_for_review(session, art_id)
    assert v_rep.passed is True

    # 3. submit_for_review - invalid previous status
    art.status = ContentArtifactStatus.APPROVED
    with pytest.raises(ValueError, match="Only generated, validation_failed, or revision_required"):
        await service.submit_for_review(session, art_id, "actor1")

    # 4. submit_for_review - validation fails
    art.status = ContentArtifactStatus.GENERATED
    factory_service.validate_existing_artifact.return_value = MagicMock(passed=False, errors=["schema error"])
    with pytest.raises(ValueError, match="Artifact validation failed"):
        await service.submit_for_review(session, art_id, "actor1")
    assert art.status == ContentArtifactStatus.VALIDATION_FAILED

    # 5. submit_for_review - success
    art.status = ContentArtifactStatus.GENERATED
    factory_service.validate_existing_artifact.return_value = MagicMock(passed=True, errors=[])
    sub_res = await service.submit_for_review(session, art_id, "actor1")
    assert isinstance(sub_res, ArtifactStatusTransition)
    assert sub_res.new_status == "pending_review"
    assert art.status == ContentArtifactStatus.PENDING_REVIEW

    # 6. reject_artifact - empty reason & success
    with pytest.raises(ValueError, match="Rejecting an artifact requires a reason"):
        await service.reject_artifact(session, art_id, "actor1", "   ")

    rej_res = await service.reject_artifact(session, art_id, "actor1", "poor quality")
    assert rej_res.new_status == "rejected"
    assert art.status == ContentArtifactStatus.REJECTED

    # 7. quarantine_artifact
    governance_service.quarantine_artifact.return_value = art
    q_res = await service.quarantine_artifact(session, art_id, "actor1", "flagged pii")
    assert q_res.new_status == "quarantined"

    # 8. retire_artifact - empty reason & success
    with pytest.raises(ValueError, match="Retiring an artifact requires a reason"):
        await service.retire_artifact(session, art_id, "actor1", "")

    ret_res = await service.retire_artifact(session, art_id, "actor1", "curriculum obsolete")
    assert ret_res.new_status == "retired"

    # 9. mark_seeded_staging - not approved or not publication eligible
    art.status = ContentArtifactStatus.PENDING_REVIEW
    with pytest.raises(ValueError, match="Only quorum-approved artifacts"):
        await service.mark_seeded_staging(session, art_id, "actor1")

    art.status = ContentArtifactStatus.APPROVED
    art.publication_eligible = False
    with pytest.raises(ValueError, match="not publication eligible"):
        await service.mark_seeded_staging(session, art_id, "actor1")

    art.publication_eligible = True
    seed_res = await service.mark_seeded_staging(session, art_id, "actor1")
    assert seed_res.new_status == "seeded_staging"
    assert art.status == ContentArtifactStatus.SEEDED_STAGING

    # 10. mark_promoted_production - not seeded_staging or not publication eligible
    art.status = ContentArtifactStatus.APPROVED
    with pytest.raises(ValueError, match="Only seeded_staging artifacts can be promoted"):
        await service.mark_promoted_production(session, art_id, "actor1")

    art.status = ContentArtifactStatus.SEEDED_STAGING
    art.publication_eligible = False
    with pytest.raises(ValueError, match="not publication eligible"):
        await service.mark_promoted_production(session, art_id, "actor1")

    art.publication_eligible = True
    prom_res = await service.mark_promoted_production(session, art_id, "actor1")
    assert prom_res.new_status == "promoted_production"
    assert art.status == ContentArtifactStatus.PROMOTED_PRODUCTION

    # _value helper
    assert _value(ContentArtifactStatus.APPROVED) == "approved"
    assert _value("approved") == "approved"


# ============================================================================
# ContentBulkReviewService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_bulk_review_service():
    lifecycle_service = AsyncMock()
    assignment_service = AsyncMock()
    service = ContentBulkReviewService(
        lifecycle_service=lifecycle_service,
        assignment_service=assignment_service,
    )
    session = AsyncMock()
    art1 = uuid.uuid4()
    art2 = uuid.uuid4()

    # 1. bulk_approve is disabled
    with pytest.raises(ValueError, match="Bulk approval is disabled by Phase 3 governance"):
        await service.bulk_approve(session, [art1], reviewer_id="rev1", notes="looks good")

    # 2. bulk_reject - empty reason
    with pytest.raises(ValueError, match="Bulk rejection requires a reason"):
        await service.bulk_reject(session, [art1], reviewer_id="rev1", reason="")

    # 3. bulk_reject - exceeding batch limit
    large_list = [uuid.uuid4() for _ in range(105)]
    with pytest.raises(ValueError, match="Bulk rejection is limited to 100 artifacts"):
        await service.bulk_reject(session, large_list, reviewer_id="rev1", reason="bad batch")

    # 4. bulk_reject - success
    lifecycle_service.reject_artifact.side_effect = [
        ArtifactStatusTransition(art1, "pending_review", "rejected", "rev1", "bad batch"),
        ArtifactStatusTransition(art2, "pending_review", "rejected", "rev1", "bad batch"),
    ]
    rej_res = await service.bulk_reject(session, [art1, art2], reviewer_id="rev1", reason="bad batch")
    assert isinstance(rej_res, BulkReviewResult)
    assert rej_res.status == "rejected"
    assert len(rej_res.artifact_ids) == 2
    assert rej_res.summary["rejected"] == 2

    # 5. bulk_quarantine - empty reason & success
    with pytest.raises(ValueError, match="Bulk quarantine requires a reason"):
        await service.bulk_quarantine(session, [art1], reviewer_id="rev1", reason="   ")

    lifecycle_service.quarantine_artifact.side_effect = [
        ArtifactStatusTransition(art1, "pending_review", "quarantined", "rev1", "quarantine reason"),
    ]
    q_res = await service.bulk_quarantine(session, [art1], reviewer_id="rev1", reason="quarantine reason")
    assert q_res.status == "quarantined"
    assert len(q_res.artifact_ids) == 1

    # 6. bulk_assign
    assignment_mock = MagicMock(artifact_id=art1)
    assignment_service.assign_batch.return_value = [assignment_mock]
    assign_res = await service.bulk_assign(session, [art1], reviewer_id="rev1", assigned_by="lead", priority="urgent")
    assert assign_res.status == "assigned"
    assert assign_res.artifact_ids == [art1]


# ============================================================================
# ContentReviewRiskService Tests
# ============================================================================
def test_content_review_risk_service():
    service = ContentReviewRiskService()

    # 1. Clean deterministic low-risk artifact
    clean_art = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        source_snapshot_hash="snap1",
        provider="deterministic",
        artifact_json={"difficulty": "medium", "answer_key_confidence": 0.95},
        sources=[
            ContentArtifactSource(
                source_id=uuid.uuid4(),
                source_quality_score=0.9,
                source_metadata={"document_status": "current"},
            )
        ],
    )
    val_clean = MagicMock(passed=True, errors=[])
    prov_clean = MagicMock(passed=True)

    risk_low = service.score_artifact(
        clean_art,
        validation_report=val_clean,
        provenance_report=prov_clean,
        prior_approved_count=5,
        duplicate_count=0,
    )
    assert isinstance(risk_low, ReviewRisk)
    assert risk_low.level == "low"
    assert risk_low.score == 0
    assert len(risk_low.reasons) == 0

    # 2. Critical risk artifact (failed provenance, low source quality, validation fail, hard difficulty, stale doc)
    dirty_source = ContentArtifactSource(
        source_id=uuid.uuid4(),
        source_quality_score=0.3,
        source_metadata={"document_status": "deprecated"},
    )
    risky_art = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        source_snapshot_hash=None,  # missing_provenance
        provider="openai",          # non_deterministic_provider (+20)
        artifact_json={"difficulty": "hard", "answer_key_confidence": 0.5},  # high_difficulty (+20), low_confidence (+25)
        sources=[dirty_source],     # low_source_quality (+35), stale_source_document (+50)
    )
    prov_fail = MagicMock(passed=False)  # invalid_provenance (+100)
    val_fail = MagicMock(passed=False, errors=["e1", "e2"])  # validation_failed (+60), validation_warnings (+20)

    risk_crit = service.score_artifact(
        risky_art,
        validation_report=val_fail,
        provenance_report=prov_fail,
        prior_approved_count=0,  # new_caps_ref (+10)
        duplicate_count=2,       # duplicate_similarity (+30)
    )
    assert risk_crit.level == "critical"
    assert risk_crit.score >= 90
    assert "invalid_provenance" in risk_crit.reasons
    assert "low_source_quality" in risk_crit.reasons
    assert "validation_failed" in risk_crit.reasons
    assert "stale_source_document" in risk_crit.reasons
    assert "duplicate_similarity" in risk_crit.reasons
    assert "new_caps_ref" in risk_crit.reasons

    # 3. Medium and high levels
    art_high = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        source_snapshot_hash="snap",
        provider="deterministic",
        artifact_json={},
        sources=[],  # missing_sources (+60)
    )
    risk_high = service.score_artifact(art_high, prior_approved_count=1)
    assert risk_high.level == "high"
    assert risk_high.score == 60

    art_med = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        source_snapshot_hash="snap",
        provider="anthropic",  # non_deterministic (+20)
        artifact_json={},
        sources=[ContentArtifactSource(source_id=uuid.uuid4(), source_quality_score=0.8)],
    )
    risk_med = service.score_artifact(art_med, prior_approved_count=1)
    assert risk_med.level == "medium"
    assert risk_med.score == 20
