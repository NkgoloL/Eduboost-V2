from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.models.content_factory import ContentArtifactStatus, ContentReviewAction
from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    SourceContextChunk,
)
from app.services.content_generation.providers.llm import LLMContentGenerationProvider
from app.services.content_review_governance import (
    ContentReviewEligibilityService,
    ContentReviewGovernanceService,
    ReviewGovernancePolicy,
)
from app.services.llm_provider import GenerationResult, TokenUsage


PASSING_RUBRIC = {
    "caps_alignment": True,
    "factual_accuracy": True,
    "answer_key_correctness": True,
    "grade_suitability": True,
    "language_quality": True,
    "cultural_appropriateness": True,
    "bias_and_safety": True,
    "accessibility_and_clarity": True,
    "source_grounding": True,
    "personal_information": True,
}


def artifact(status: str, eligible: bool = True):
    return SimpleNamespace(
        status=status,
        publication_eligible=eligible,
        published_at=object() if status == "published" else None,
    )


def test_policy_rejects_unsafe_quorum(monkeypatch) -> None:
    monkeypatch.setenv("CONTENT_CONSENSUS_THRESHOLD", "1")
    with pytest.raises(ValueError, match="between 2 and 10"):
        ReviewGovernancePolicy.from_environment()


def test_approval_requires_complete_passing_rubric() -> None:
    service = ContentReviewGovernanceService(policy=ReviewGovernancePolicy())
    with pytest.raises(ValueError, match="incomplete"):
        service._validate_decision_input(
            action=ContentReviewAction.APPROVE,
            rubric_results={"caps_alignment": True},
            reason_code=None,
        )
    failed = dict(PASSING_RUBRIC)
    failed["factual_accuracy"] = False
    with pytest.raises(ValueError, match="rubric failures"):
        service._validate_decision_input(
            action=ContentReviewAction.APPROVE,
            rubric_results=failed,
            reason_code=None,
        )
    service._validate_decision_input(
        action=ContentReviewAction.APPROVE,
        rubric_results=PASSING_RUBRIC,
        reason_code=None,
    )


def test_non_approval_decisions_require_reason_code() -> None:
    service = ContentReviewGovernanceService(policy=ReviewGovernancePolicy())
    with pytest.raises(ValueError, match="reason code"):
        service._validate_decision_input(
            action=ContentReviewAction.REJECT,
            rubric_results={},
            reason_code=None,
        )


def test_eligibility_is_fail_closed() -> None:
    assert not ContentReviewEligibilityService.is_retrieval_eligible(
        artifact(ContentArtifactStatus.APPROVED.value)
    )
    assert not ContentReviewEligibilityService.is_retrieval_eligible(
        artifact(ContentArtifactStatus.QUARANTINED.value)
    )
    assert ContentReviewEligibilityService.is_retrieval_eligible(
        artifact(ContentArtifactStatus.PROMOTED_PRODUCTION.value)
    )
    assert ContentReviewEligibilityService.is_learner_eligible(
        artifact(ContentArtifactStatus.PUBLISHED.value)
    )


class FakeRouter:
    async def generate(self, **kwargs):
        del kwargs
        return GenerationResult(
            text=json.dumps(
                {
                    "items": [
                        {
                            "question_text": "What is the value of the digit 5 in 5 432?",
                            "options": ["5", "50", "500", "5 000"],
                            "correct_answer": "5 000",
                            "explanation": "The digit 5 is in the thousands place, so its value is 5 000.",
                            "difficulty": "easy",
                            "cognitive_level": "understand",
                        }
                    ]
                }
            ),
            provider="deterministic-test",
            model="test",
            usage=TokenUsage(10, 20, 30, 0.0),
            latency_ms=1.0,
        )


@pytest.mark.asyncio
async def test_phase1_canonical_llm_adapter_uses_real_request_contract() -> None:
    provider = LLMContentGenerationProvider(router=FakeRouter())
    request = DiagnosticGenerationRequest(
        scope_id="g4-math",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        topic_title="Whole numbers",
        required_count=1,
        approved_count=0,
        missing_count=1,
        source_chunks=[
            SourceContextChunk(
                source_document_id="caps",
                source_chunk_id="whole-numbers",
                text="The digit in the thousands place represents thousands.",
                document_status="approved",
            )
        ],
    )
    items = await provider.generate_diagnostic_items(request)
    assert len(items) == 1
    assert items[0].correct_answer == "5 000"
    assert items[0].source_chunk_ids == ["whole-numbers"]

@pytest.mark.asyncio
async def test_stale_review_processing_never_auto_approves() -> None:
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    assignment = SimpleNamespace(
        reminder_count=0,
        last_reminded_at=None,
        escalated_at=None,
        due_by=now - __import__("datetime").timedelta(hours=200),
        assigned_at=now - __import__("datetime").timedelta(hours=200),
        status="assigned",
    )
    service = ContentReviewGovernanceService(policy=ReviewGovernancePolicy(stale_after_hours=72))

    async def stale(*args, **kwargs):
        del args, kwargs
        return [assignment]

    service.list_stale_assignments = stale

    class Session:
        async def flush(self):
            return None

    result = await service.process_stale_assignments(Session(), now=now)
    assert result == {"stale": 1, "reminded": 1, "escalated": 1}
    assert assignment.status == "assigned"
    assert assignment.reminder_count == 1


def test_phase3_arq_job_is_registered() -> None:
    from app.modules.jobs import WorkerSettings

    assert any(
        getattr(function, "__name__", "") == "process_stale_content_reviews"
        for function in WorkerSettings.functions
    )
