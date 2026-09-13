"""Comprehensive unit tests covering content file review workflow, review queue, and review risk services."""
from datetime import datetime, timezone
import json
from pathlib import Path

from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAssignment,
    ContentValidationReport,
)
from app.services.content_file_review_workflow import (
    ContentFileReviewWorkflowService,
    ScopeReviewEvidenceStatus,
    _dev_approved_decision,
    _educator_approved_decision,
    _legal_approved_decision,
    _now_utc,
    _pending,
    _stage_unlocked_decision,
    _valid_evidence_url,
    _write_json,
)
from app.services.content_review_queue import (
    ArtifactReviewBundle,
    ContentReviewQueueService,
    ReviewQueueItem,
    ReviewQueuePage,
    ReviewSummary,
    _artifact_dict,
    _review_dict,
    _validation_dict,
)

from app.services.content_review_risk import (
    ContentReviewRiskService,
    ReviewRisk,
)


# ============================================================================
# ContentReviewRiskService Tests
# ============================================================================
def test_content_review_risk_service():
    service = ContentReviewRiskService()

    # 1. Critical risk (provenance failed or missing)
    art_no_prov = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        source_snapshot_hash=None,
        sources=[],
    )
    risk_no_prov = service.score_artifact(art_no_prov)
    assert risk_no_prov.level == "critical"
    assert "missing_provenance" in risk_no_prov.reasons
    assert "missing_sources" in risk_no_prov.reasons

    # Provenance report passed=False
    prov_rep_fail = MagicMock(passed=False)
    risk_prov_fail = service.score_artifact(
        ContentGenerationArtifact(source_snapshot_hash="h1", sources=[]),
        provenance_report=prov_rep_fail,
    )
    assert "invalid_provenance" in risk_prov_fail.reasons

    # 2. Validation report failed and warnings
    val_rep_fail = MagicMock(passed=False, errors=["err1", "err2", "err3", "err4"])
    source_low = MagicMock(source_quality_score=0.3, source_metadata={"document_status": "deprecated"})
    art_complex = ContentGenerationArtifact(
        source_snapshot_hash="h1",
        sources=[source_low],
        provider="anthropic-claude",
        artifact_json={"difficulty": "hard", "answer_key_confidence": 0.5},
    )
    prov_rep_ok = MagicMock(passed=True)
    risk_complex = service.score_artifact(
        art_complex,
        validation_report=val_rep_fail,
        provenance_report=prov_rep_ok,
        prior_approved_count=0,
        duplicate_count=2,
    )
    assert risk_complex.level == "critical"
    assert "validation_failed" in risk_complex.reasons
    assert "validation_warnings" in risk_complex.reasons
    assert "low_source_quality" in risk_complex.reasons
    assert "non_deterministic_provider" in risk_complex.reasons
    assert "high_difficulty" in risk_complex.reasons
    assert "low_confidence_answer_key" in risk_complex.reasons
    assert "new_caps_ref" in risk_complex.reasons
    assert "duplicate_similarity" in risk_complex.reasons
    assert "stale_source_document" in risk_complex.reasons

    # 3. Clean low risk artifact
    source_good = MagicMock(source_quality_score=0.9, source_metadata={"document_status": "current"})
    art_clean = ContentGenerationArtifact(
        source_snapshot_hash="h1",
        sources=[source_good],
        provider="deterministic",
        artifact_json={"difficulty": "easy", "answer_key_confidence": 0.99},
    )
    val_rep_ok = MagicMock(passed=True, errors=[])
    risk_clean = service.score_artifact(
        art_clean,
        validation_report=val_rep_ok,
        provenance_report=prov_rep_ok,
        prior_approved_count=10,
        duplicate_count=0,
    )
    assert risk_clean.level == "low"
    assert risk_clean.score == 0

    # 4. Medium / High boundaries
    # Medium boundary (score >= 20, < 50)
    art_medium = ContentGenerationArtifact(
        source_snapshot_hash="h1",
        sources=[source_good],
        provider="openai-gpt4",  # +20
        artifact_json={},
    )
    risk_medium = service.score_artifact(
        art_medium,
        validation_report=val_rep_ok,
        provenance_report=prov_rep_ok,
        prior_approved_count=5,
    )
    assert risk_medium.level == "medium"

    # High boundary (score >= 50, < 90)
    source_stale_only = MagicMock(source_quality_score=0.8, source_metadata={"document_status": "stale"})
    art_high = ContentGenerationArtifact(
        source_snapshot_hash="h1",
        sources=[source_stale_only],  # +50
        provider="deterministic",
        artifact_json={},
    )
    risk_high = service.score_artifact(
        art_high,
        validation_report=val_rep_ok,
        provenance_report=prov_rep_ok,
        prior_approved_count=5,
    )
    assert risk_high.level == "high"


# ============================================================================
# ContentReviewQueueService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_review_queue_service():
    risk_service = MagicMock()
    factory_service = AsyncMock()

    service = ContentReviewQueueService(
        risk_service=risk_service,
        factory_service=factory_service,
    )
    session = AsyncMock()

    art_id = uuid.uuid4()
    scope_id = "scope_math_g4"

    art = ContentGenerationArtifact(
        artifact_id=art_id,
        scope_id=scope_id,
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        caps_ref="4.M.1",
        status=ContentArtifactStatus.PENDING_REVIEW,
        provider="deterministic",
        model="test-model",
        prompt_version="1.0",
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        reviews=[],
    )

    assignment = ContentReviewAssignment(
        artifact_id=art_id,
        assigned_to="reviewer_1",
    )
    val_report = ContentValidationReport(
        artifact_id=art_id,
        passed=True,
        errors=[],
    )

    # 1. list_queue and get_review_summary
    session.execute.side_effect = [
        # Base query for artifacts
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[art])))),
        # _load_assignments
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[assignment])))),
        # _latest_validation_reports
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[val_report])))),
        # Count query
        MagicMock(scalar_one=MagicMock(return_value=1)),
    ]
    provenance = MagicMock(passed=True, errors=[], sources=[], source_snapshot_hash="snap")
    factory_service.get_artifact_provenance.return_value = provenance
    risk_service.score_artifact.return_value = ReviewRisk(level="low", score=5, reasons=[])

    page = await service.list_queue(
        session,
        scope_id=scope_id,
        layer="diagnostic_items",
        caps_ref="4.M.1",
        artifact_type="diagnostic_item",
        risk_level="low",
        reviewer_id="reviewer_1",
    )
    assert isinstance(page, ReviewQueuePage)
    assert page.total == 1
    assert len(page.items) == 1
    assert page.items[0].reviewer_id == "reviewer_1"

    # Review summary
    service.list_queue = AsyncMock(return_value=page)
    summary = await service.get_review_summary(session, scope_id=scope_id)
    assert isinstance(summary, ReviewSummary)
    assert summary.low_risk == 1

    # 2. get_artifact_review_bundle
    factory_service.get_artifact.return_value = art
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[val_report])))),
    ]
    bundle = await service.get_artifact_review_bundle(session, art_id)
    assert isinstance(bundle, ArtifactReviewBundle)
    assert bundle.artifact["artifact_id"] == str(art_id)
    assert bundle.validation_report is not None

    # Helper serializers
    assert _artifact_dict(art)["status"] == "pending_review"
    assert _validation_dict(val_report)["passed"] is True
    assert _review_dict(MagicMock(review_id=uuid.uuid4(), review_action="approved", review_reason="ok", reviewer_id="user1"))["review_action"] == "approved"



# ============================================================================
# ContentFileReviewWorkflowService Tests
# ============================================================================
def test_content_file_review_workflow_service(tmp_path: Path):
    registry = MagicMock()
    readiness_service = MagicMock()
    manifest_dir = tmp_path / "review_manifests"

    service = ContentFileReviewWorkflowService(
        project_root=tmp_path,
        registry=registry,
        readiness_service=readiness_service,
        manifest_dir=manifest_dir,
    )

    scope_id = "scope_math_g4"
    mock_scope = MagicMock(
        scope_id=scope_id,
        status=MagicMock(value="active"),
        review_policy_id="policy_v1",
    )
    registry.get_scope.return_value = mock_scope

    # 1. Missing review packet check
    missing_status = service.review_status("non_existent_scope", manifest_dir=manifest_dir)
    assert isinstance(missing_status, ScopeReviewEvidenceStatus)
    assert missing_status.status == "missing"
    assert missing_status.stage_unlocked is False

    # 2. build_review_packet (dev_approved decision)
    readiness_service.evaluate_scope.return_value = MagicMock(
        manifest={
            "staging_eligible": True,
            "production_eligible": False,
            "blockers": [],
            "layers": {
                "diagnostic_items": {
                    "relative_path": "diag.json",
                    "sha256": "h123",
                    "record_count": 10,
                    "review_ready_count": 10,
                }
            },
        }
    )

    packet_dev = service.build_review_packet(
        scope_id=scope_id,
        reviewer_id="rev_1",
        decision="dev_approved",
        evidence_url="https://gov.eduboost.org/reviews/123",
        notes="Testing dev approval",
        output_dir=manifest_dir,
    )
    assert packet_dev["dev_approved"] is True
    assert packet_dev["stage_unlocked"] is True

    status_dev = service.review_status(scope_id, manifest_dir=manifest_dir)
    assert status_dev.status == "dev_approved"
    assert status_dev.stage_unlocked is True
    assert status_dev.production_unlocked is False

    # 3. build_review_packet (fully approved for production)
    packet_prod = service.build_review_packet(
        scope_id=scope_id,
        reviewer_id="rev_1",
        decision="approved",
        evidence_url="https://gov.eduboost.org/reviews/123",
        legal_decision="approved",
        legal_evidence_url="https://legal.eduboost.org/audits/456",
        notes="Full educator and legal approval",
        output_dir=manifest_dir,
    )
    assert packet_prod["approved"] is True
    assert packet_prod["legal_approved"] is True

    status_prod = service.review_status(scope_id, manifest_dir=manifest_dir)
    assert status_prod.status == "approved"
    assert status_prod.stage_unlocked is True
    assert status_prod.production_unlocked is True
    assert not status_prod.blockers

    # 4. build_review_packet (pending review / placeholder URL stage blockers)
    service.build_review_packet(
        scope_id=scope_id,
        reviewer_id="pending",
        decision="pending",
        evidence_url="http://example.com/fake",
        legal_decision="pending",
        legal_evidence_url="pending",
        notes="Pending",
        output_dir=manifest_dir,
    )
    status_pending = service.review_status(scope_id, manifest_dir=manifest_dir)
    assert status_pending.status == "pending"
    assert status_pending.stage_unlocked is False
    assert any("Review decision is not dev_approved or approved." in b for b in status_pending.stage_blockers)
    assert any("Reviewer ID is pending." in b for b in status_pending.stage_blockers)

    # 5. Invalid layer records & sha256
    corrupted_manifest = tmp_path / "review_manifests" / f"{scope_id}_educator_review.json"
    data = json.loads(corrupted_manifest.read_text(encoding="utf-8"))
    data["layer_review"] = {"diagnostic_items": {"record_count": 0, "sha256": ""}}
    data["decision"] = "dev_approved"
    data["reviewer_id"] = "rev_ok"
    data["evidence_url"] = "https://gov.eduboost.org/proof"
    data["approved_at"] = "2026-01-01T00:00:00Z"
    _write_json(corrupted_manifest, data)
    status_corrupt = service.review_status(scope_id, manifest_dir=manifest_dir)
    assert any("has no records" in b for b in status_corrupt.stage_blockers)
    assert any("missing artifact hash" in b for b in status_corrupt.stage_blockers)

    # 6. Decisions, URL and time helpers
    assert _stage_unlocked_decision("dev_approved") is True
    assert _stage_unlocked_decision("approved") is True
    assert _stage_unlocked_decision("rejected") is False
    assert _dev_approved_decision("dev_approved") is True
    assert _educator_approved_decision("accepted") is True
    assert _legal_approved_decision("pass") is True
    assert _pending("null") is True
    assert _pending("something") is False
    assert _valid_evidence_url("https://real.evidence.org/doc") is True
    assert _valid_evidence_url("https://localhost/doc") is False
    assert _valid_evidence_url("http://insecure.org/doc") is False
    assert _now_utc().endswith("Z")

