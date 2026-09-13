from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.assessment_service_v2 import AssessmentServiceV2
from app.services.mastery_engine import (
    MAX_CONFIDENCE_THRESHOLD,
    MasteryBoundError,
    MasteryEngine,
    MasteryEstimate,
    MasteryStateEnum,
    assert_no_authoritative_claims,
)


@pytest.mark.asyncio
async def test_assessment_service_v2():
    mock_repo = MagicMock()
    mock_repo.list_assessments = AsyncMock(return_value=[{"id": "a1", "title": "Math Grade 4"}])
    mock_repo.get_assessment = AsyncMock(
        return_value={
            "id": "a1",
            "total_marks": 10,
            "questions": [
                {"question_id": "q1", "correct_answer": "42", "marks": 5},
                {"question_id": "q2", "correct_answer": "b", "marks": 5},
            ],
        }
    )
    mock_repo.create_attempt = AsyncMock(return_value="att_999")

    mock_audit = MagicMock()
    mock_audit.log_event = AsyncMock()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.assessment_service_v2.AuditService", lambda: mock_audit)

        svc = AssessmentServiceV2(repository=mock_repo)
        
        # with_db chaining
        mock_db = MagicMock()
        assert svc.with_db(mock_db) is svc
        assert svc.db is mock_db

        # 1. list_assessments
        listed = await svc.list_assessments(limit=10, offset=0)
        assert len(listed["assessments"]) == 1
        assert mock_audit.log_event.await_count == 1

        # 2. submit_attempt - correct
        attempt_res = await svc.submit_attempt(
            assessment_id="a1",
            learner_id="l1",
            responses=[
                {"question_id": "q1", "learner_answer": "42"},
                {"question_id": "q2", "selected_option": "B"},
            ],
            time_taken_seconds=120,
        )
        assert attempt_res["attempt_id"] == "att_999"
        assert attempt_res["correct_count"] == 2
        assert attempt_res["marks_obtained"] == 10
        assert attempt_res["score"] == 1.0

        # 3. submit_attempt - assessment not found
        mock_repo.get_assessment = AsyncMock(return_value=None)
        with pytest.raises(ValueError, match="Assessment not found"):
            await svc.submit_attempt("missing", "l1", [])


def test_mastery_engine_and_bounds():
    engine = MasteryEngine()

    # 1. Invalid response counts
    with pytest.raises(ValueError, match="Invalid response counts"):
        engine.calculate_node_mastery("l1", "n1", correct_responses=5, total_responses=2)

    with pytest.raises(ValueError, match="Invalid response counts"):
        engine.calculate_node_mastery("l1", "n1", correct_responses=-1, total_responses=2)

    # 2. total_responses == 0
    est_zero_no_prior = engine.calculate_node_mastery("l1", "n1", correct_responses=0, total_responses=0)
    assert est_zero_no_prior.mastery_score == 0.0
    assert est_zero_no_prior.confidence == 0.0
    assert est_zero_no_prior.state == MasteryStateEnum.TENTATIVE

    est_zero_with_prior = engine.calculate_node_mastery(
        "l1", "n1", correct_responses=0, total_responses=0, prior_score=0.85
    )
    assert est_zero_with_prior.mastery_score == 0.85
    assert est_zero_with_prior.confidence == 0.10

    # 3. Observed direct responses (bounded confidence)
    est_direct = engine.calculate_node_mastery("l1", "n1", correct_responses=10, total_responses=10)
    assert est_direct.mastery_score == 1.0
    assert est_direct.confidence <= MAX_CONFIDENCE_THRESHOLD
    assert est_direct.state == MasteryStateEnum.TENTATIVE

    # 4. Inferred prerequisite
    est_inferred = engine.calculate_node_mastery(
        "l1", "n1", correct_responses=8, total_responses=10, is_prerequisite_inferred=True
    )
    assert est_inferred.state == MasteryStateEnum.INFERRED

    # 5. Serialization
    d = est_direct.to_dict()
    assert d["learner_id"] == "l1"
    assert "computed_at" in d

    # 6. assert_no_authoritative_claims
    # Empty args
    with pytest.raises(ValueError, match="requires at least one"):
        assert_no_authoritative_claims()

    # Authoritative state rejected
    with pytest.raises(MasteryBoundError, match="authoritative"):
        assert_no_authoritative_claims(state=MasteryStateEnum.AUTHORITATIVE)

    with pytest.raises(MasteryBoundError, match="authoritative"):
        assert_no_authoritative_claims(state="authoritative")

    with pytest.raises(MasteryBoundError, match="authoritative"):
        assert_no_authoritative_claims(estimate={"state": "authoritative"})

    # Exceeding confidence ceiling
    with pytest.raises(MasteryBoundError, match="exceeds approved ceiling"):
        assert_no_authoritative_claims(confidence=0.99)

    with pytest.raises(MasteryBoundError, match="exceeds approved ceiling"):
        assert_no_authoritative_claims(estimate={"confidence": 0.85})

    with pytest.raises(MasteryBoundError, match="exceeds approved ceiling"):
        assert_no_authoritative_claims(estimate=0.75)

    # Invalid confidence string
    with pytest.raises(ValueError, match="Invalid confidence value"):
        assert_no_authoritative_claims(confidence="not_a_number")

    # Valid claims pass without error
    assert_no_authoritative_claims(estimate=est_direct)
    assert_no_authoritative_claims(confidence=0.55, state=MasteryStateEnum.TENTATIVE)
