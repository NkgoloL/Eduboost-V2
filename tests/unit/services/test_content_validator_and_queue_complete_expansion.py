import json
import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel, Field

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAssignment,
    ContentValidationReport,
    ContentArtifactReview,
)
from app.services.content_validator import ContentValidator, ValidationResult
from app.services.content_review_queue import (
    ContentReviewQueueService,
    ReviewQueuePage,
    ReviewSummary,
    ArtifactReviewBundle,
    _review_dict,
)


def test_content_validator_custom_and_unknown_schema():
    validator = ContentValidator()

    # 1. Unknown content_type through public validate()
    res_unknown = validator.validate('{"key": "val"}', content_type="nonexistent_type")
    assert res_unknown.passed is False
    assert any("Unknown content type" in e for e in res_unknown.errors)

    # 2. _dispatch fallback where content type has schema version but not schema class
    res_no_cls = validator._dispatch("unknown_registered", "1.0", {"a": 1}, None)
    assert res_no_cls.passed is False
    assert any("No validator for content type" in e for e in res_no_cls.errors)

    # 3. Custom schema success & validation failure via patched schemas
    class SampleModel(BaseModel):
        title: str = Field(min_length=3)
        count: int

    with (
        patch("app.services.content_validator.CONTENT_TYPE_SCHEMAS", {"sample": SampleModel}),
        patch("app.services.content_validator.get_schema_version", return_value="1.0"),
    ):
        # Valid payload
        res_valid = validator.validate('{"title": "Valid Title", "count": 5}', content_type="sample")
        assert res_valid.passed is True
        assert res_valid.validated_payload.title == "Valid Title"

        # Invalid payload (triggers ValidationError in _dispatch)
        res_invalid = validator.validate('{"title": "x", "count": "not_an_int"}', content_type="sample")
        assert res_invalid.passed is False
        assert len(res_invalid.errors) > 0
        assert "validation_schema_failed" in res_invalid.error_summary or len(res_invalid.errors) >= 1

    # 4. Diagnostic batch with caps_ref mismatch (hits line 187)
    item_payload = {
        "question": "What is two plus two in base 10?",
        "options": ["3", "4", "5"],
        "correct_answer_index": 1,
        "explanation": "Two plus two equals four under standard arithmetic rules.",
        "bloom_level": "knowledge",
        "difficulty_band": "easy",
        "caps_ref": "4.M.1",
    }
    raw_batch = json.dumps([item_payload])
    res_mismatch = validator.validate(raw_batch, content_type="diagnostic_item", caps_ref="5.M.9")
    assert res_mismatch.passed is False
    assert any("does not match expected '5.M.9'" in e for e in res_mismatch.errors)



@pytest.mark.asyncio
async def test_content_review_queue_filtering_and_bundle_reviews():
    service = ContentReviewQueueService()
    session = AsyncMock()

    aid1 = uuid.uuid4()
    aid2 = uuid.uuid4()

    art1 = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid1,
        scope_id="scope-1",
        content_layer="lessons",
        artifact_type="lesson",
        caps_ref="4.M.1",
        status=ContentArtifactStatus.PENDING_REVIEW,
        artifact_json={"title": "L1"},
        provider="deterministic",
        model=None,
        prompt_version="v1",
        run_id=None,
        task_id=None,
        created_at=datetime.now(timezone.utc),
    )
    rev1 = MagicMock(
        spec=ContentArtifactReview,
        review_id=uuid.uuid4(),
        review_action="approve",
        review_reason="Looks good",
        reviewer_id="reviewer-1",
    )
    art1.reviews = [rev1]

    art2 = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid2,
        scope_id="scope-1",
        content_layer="lessons",
        artifact_type="lesson",
        caps_ref="4.M.1",
        status=ContentArtifactStatus.PENDING_REVIEW,
        artifact_json={"title": "L2"},
        provider="deterministic",
        model=None,
        prompt_version="v1",
        run_id=None,
        task_id=None,
        created_at=datetime.now(timezone.utc),
    )
    art2.reviews = []

    # Mock query results
    mock_res_arts = MagicMock()
    mock_res_arts.scalars.return_value.all.return_value = [art1, art2]

    mock_res_count = MagicMock()
    mock_res_count.scalar_one.return_value = 2

    session.execute.side_effect = [mock_res_arts, mock_res_count]

    # Assignments: both assigned to rev-1
    assign1 = MagicMock(spec=ContentReviewAssignment, artifact_id=aid1, assigned_to="rev-1")
    assign2 = MagicMock(spec=ContentReviewAssignment, artifact_id=aid2, assigned_to="rev-1")
    service._load_assignments = AsyncMock(return_value={aid1: assign1, aid2: assign2})

    # Validation report: art1 passed
    val1 = MagicMock(spec=ContentValidationReport, artifact_id=aid1, passed=True, checks=[], errors=[])
    service._latest_validation_reports = AsyncMock(return_value={aid1: val1})

    # Provenance
    mock_prov = MagicMock(passed=True, errors=[], source_snapshot_hash="snap-1", sources=[])
    service.factory_service = MagicMock()
    service.factory_service.get_artifact_provenance = AsyncMock(return_value=mock_prov)

    # Risk service: art1 has high risk, art2 has low risk
    risk_high = MagicMock(level="high", reasons=["reason1"])
    risk_low = MagicMock(level="low", reasons=[])

    def mock_score(art, **kwargs):
        if art.artifact_id == aid1:
            return risk_high
        return risk_low

    service.risk_service = MagicMock()
    service.risk_service.score_artifact.side_effect = mock_score

    # Filter with reviewer_id="rev-1" and risk_level="high" -> art2 should hit line 100 continue
    page = await service.list_queue(
        session,
        scope_id="scope-1",
        layer="lessons",
        caps_ref="4.M.1",
        artifact_type="lesson",
        reviewer_id="rev-1",
        risk_level="high",
        limit=10,
        offset=0,
    )
    assert len(page.items) == 1
    assert page.items[0].artifact_id == aid1
    assert page.items[0].reviewer_id == "rev-1"

    # 2. get_review_summary
    session.execute.side_effect = [mock_res_arts, mock_res_count]
    summary = await service.get_review_summary(session, scope_id="scope-1")
    assert summary.pending_review >= 1

    # 3. get_artifact_review_bundle with prior_review_events
    service.factory_service.get_artifact = AsyncMock(return_value=art1)
    bundle = await service.get_artifact_review_bundle(session, aid1)
    assert len(bundle.prior_review_events) == 1
    assert bundle.prior_review_events[0]["review_action"] == "approve"

    # 4. Test unmocked _load_assignments and _latest_validation_reports
    clean_service = ContentReviewQueueService()
    # Empty lists
    assert await clean_service._load_assignments(session, []) == {}
    assert await clean_service._latest_validation_reports(session, []) == {}

    # Non-empty lists
    mock_assign = MagicMock(spec=ContentReviewAssignment, artifact_id=aid1, status="assigned", assigned_to="rev-1")
    mock_res_assign = MagicMock()
    mock_res_assign.scalars.return_value.all.return_value = [mock_assign]

    mock_rep = MagicMock(spec=ContentValidationReport, artifact_id=aid1, created_at=datetime.now(timezone.utc))
    mock_res_rep = MagicMock()
    mock_res_rep.scalars.return_value.all.return_value = [mock_rep]

    session.execute.side_effect = [mock_res_assign, mock_res_rep]
    loaded_assigns = await clean_service._load_assignments(session, [aid1])
    assert aid1 in loaded_assigns
    loaded_reps = await clean_service._latest_validation_reports(session, [aid1])
    assert aid1 in loaded_reps

    # 5. Reviewer mismatch branch (line 96)
    assign2.assigned_to = "other-rev"
    session.execute.side_effect = [mock_res_arts, mock_res_count]
    page_mismatch = await service.list_queue(
        session,
        scope_id="scope-1",
        reviewer_id="rev-1",
        limit=10,
        offset=0,
    )
    assert len(page_mismatch.items) == 1

    # 6. _review_dict helper
    rev_dict = _review_dict(rev1)
    assert rev_dict["reviewer_id"] == "reviewer-1"
    assert rev_dict["review_action"] == "approve"

