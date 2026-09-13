import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.content_factory import (
    ContentGenerationArtifact,
    ContentArtifactSource,
    ContentReviewAssignment,
)
from app.services.content_review_risk import ContentReviewRiskService, ReviewRisk
from app.services.content_reviewer_assignment import ContentReviewerAssignmentService


def test_content_review_risk_scoring_all_branches():
    service = ContentReviewRiskService()

    # 1. invalid_provenance via provenance_report.passed == False
    prov_rep_bad = MagicMock(passed=False)
    art1 = MagicMock(
        spec=ContentGenerationArtifact,
        source_snapshot_hash="hash-1",
        sources=[],
        provider="deterministic",
        artifact_json={},
    )
    r1 = service.score_artifact(art1, provenance_report=prov_rep_bad)
    assert r1.level == "critical"
    assert "invalid_provenance" in r1.reasons
    assert "missing_sources" in r1.reasons

    # 2. low_source_quality and stale_source_document
    src_bad_qual = MagicMock(
        spec=ContentArtifactSource,
        source_quality_score=0.4,
        source_metadata={"document_status": "archived"},
    )
    art2 = MagicMock(
        spec=ContentGenerationArtifact,
        source_snapshot_hash="hash-2",
        sources=[src_bad_qual],
        provider="openai",  # non_deterministic_provider
        artifact_json={"difficulty": "advanced", "answer_key_confidence": 0.6},
    )
    val_rep_warn = MagicMock(passed=True, errors=["Warning 1", "Warning 2"])
    r2 = service.score_artifact(
        art2,
        validation_report=val_rep_warn,
        duplicate_count=2,
        prior_approved_count=0,
    )
    assert "low_source_quality" in r2.reasons
    assert "stale_source_document" in r2.reasons
    assert "non_deterministic_provider" in r2.reasons
    assert "high_difficulty" in r2.reasons
    assert "low_confidence_answer_key" in r2.reasons
    assert "duplicate_similarity" in r2.reasons
    assert "new_caps_ref" in r2.reasons
    assert "validation_warnings" in r2.reasons

    # 3. Score level branches: high (>=50, <90)
    art3 = MagicMock(
        spec=ContentGenerationArtifact,
        source_snapshot_hash="hash-3",
        sources=[MagicMock(source_quality_score=0.9, source_metadata={"document_status": "approved"})],
        provider="deterministic",
        artifact_json={},
    )
    # validation_failed adds 60 -> total 60 (high)
    val_failed = MagicMock(passed=False, errors=[])
    r3 = service.score_artifact(art3, validation_report=val_failed, prior_approved_count=5)
    assert r3.level == "high"

    # 4. Score level branches: medium (>=20, <50)
    # provider non_deterministic adds 20
    art4 = MagicMock(
        spec=ContentGenerationArtifact,
        source_snapshot_hash="hash-4",
        sources=[MagicMock(source_quality_score=0.9, source_metadata={"document_status": "approved"})],
        provider="llm_mock",
        artifact_json={},
    )
    r4 = service.score_artifact(art4, prior_approved_count=5)
    assert r4.level == "medium"

    # 5. Score level branches: low (<20)
    art5 = MagicMock(
        spec=ContentGenerationArtifact,
        source_snapshot_hash="hash-5",
        sources=[MagicMock(source_quality_score=0.9, source_metadata={"document_status": "approved"})],
        provider="deterministic",
        artifact_json={},
    )
    r5 = service.score_artifact(art5, prior_approved_count=5)
    assert r5.level == "low"
    assert r5.score == 0


@pytest.mark.asyncio
async def test_content_reviewer_assignment_list_and_open():
    service = ContentReviewerAssignmentService()
    session = AsyncMock()

    assignment = MagicMock(spec=ContentReviewAssignment)
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [assignment]
    mock_res.scalar_one_or_none.return_value = assignment
    session.execute.return_value = mock_res

    # 1. list_assignments with reviewer_id and status
    res_list = await service.list_assignments(session, reviewer_id="rev-1", status="assigned", limit=50)
    assert len(res_list) == 1

    # 2. list_assignments without filters
    res_list_no_filter = await service.list_assignments(session)
    assert len(res_list_no_filter) == 1

    # 3. _open_assignment with reviewer_id
    aid = uuid.uuid4()
    open_assigned = await service._open_assignment(session, aid, reviewer_id="rev-1")
    assert open_assigned == assignment

    # 4. _open_assignment without reviewer_id
    open_unassigned = await service._open_assignment(session, aid, reviewer_id=None)
    assert open_unassigned == assignment
