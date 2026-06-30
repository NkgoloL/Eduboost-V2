from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.services.content_safety.lesson_contracts import (
    CAPS_TOPIC_MAP,
    LessonOutput,
    arithmetic_expression_is_correct,
    validate_lesson_output,
)
from app.services.content_safety.pii import build_llm_context, scrub_feedback_for_rlhf
from app.services.llm.gateway import CanonicalLLMGateway, DeterministicMockProvider, LLMGatewayRequest
from scripts.check_ai_llm_safety_caps_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_ai_llm_safety_caps_repo_evidence_check_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_ai_llm_safety_caps_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_ai_llm_safety_caps_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "AI, LLM safety, lesson generation, and CAPS validation" in result.stdout


@pytest.mark.unit
def test_canonical_llm_gateway_returns_required_metadata() -> None:
    gateway = CanonicalLLMGateway([DeterministicMockProvider()])
    response = gateway.complete(
        LLMGatewayRequest(
            prompt="Generate a grade 4 fractions lesson for pseudonym LRN-001.",
            pseudonym_id="LRN-001",
            prompt_template_version="lesson-generation-v1",
            input_schema="lesson-request-v1",
            output_schema="lesson-output-v1",
        )
    )
    metadata = response.metadata
    assert metadata.provider_name == "deterministic_mock"
    assert metadata.model_version == "mock-lesson-v1"
    assert metadata.prompt_template_version == "lesson-generation-v1"
    assert metadata.input_schema == "lesson-request-v1"
    assert metadata.output_schema == "lesson-output-v1"
    assert metadata.latency_ms >= 0
    assert metadata.token_usage["total_tokens"] >= 2
    assert metadata.safety_status == "safe"
    assert metadata.fallback_status in {"primary", "development_fallback", "provider_fallback", "recovered_after_retry"}
    assert metadata.budget_status == "within_budget"


@pytest.mark.unit
def test_prompt_context_uses_pseudonym_and_scrubs_pii() -> None:
    context = build_llm_context(
        pseudonym_id="pseudo-123",
        learner_profile={
            "learner_name": "Actual Learner",
            "guardian_name": "Actual Guardian",
            "email": "guardian@example.com",
            "phone": "0821234567",
            "address": "12 Main Street",
            "learner_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "grade": 4,
        },
        learning_context={"topic": "Fractions", "note": "Call 0821234567 or email learner@example.com"},
    )
    serialized = json.dumps(context)
    assert "pseudo-123" in serialized
    assert "Actual Learner" not in serialized
    assert "Actual Guardian" not in serialized
    assert "guardian@example.com" not in serialized
    assert "0821234567" not in serialized
    assert "123e4567-e89b-12d3-a456-426614174000" not in serialized
    assert "[redacted-phone]" in serialized
    assert "[redacted-email]" in serialized


@pytest.mark.unit
def test_rlhf_feedback_requires_consent_and_scrubs_pii() -> None:
    with pytest.raises(PermissionError):
        scrub_feedback_for_rlhf({"comment": "learner@example.com"}, consent_granted=False)
    scrubbed = scrub_feedback_for_rlhf({"comment": "learner@example.com liked it", "phone": "0821234567"}, consent_granted=True)
    serialized = json.dumps(scrubbed)
    assert "learner@example.com" not in serialized
    assert "0821234567" not in serialized
    assert scrubbed["pii_scrubbed"] is True
    assert scrubbed["rlhf_schema_version"] == "rlhf-feedback-v1"


@pytest.mark.unit
def test_lesson_output_accepts_safe_caps_aligned_content() -> None:
    lesson = LessonOutput(
        topic="Numbers, operations and relationships",
        grade=4,
        subject="Mathematics",
        caps_reference="CAPS-MATH-G4-T1-FRACTIONS",
        objectives=["Compare common fractions"],
        explanation="Fractions show equal parts of a whole using a South African classroom sharing example.",
        worked_examples=["1/2 is the same as two quarters when sharing vetkoek equally."],
        practice_questions=["Which is larger: 1/2 or 1/4?"],
        answer_key=["1/2"],
        remediation_hints=["Draw the same whole and shade each fraction."],
        difficulty="core",
        language_level="intermediate",
        safety_classification="safe",
        alignment_confidence=0.92,
        quality_score=0.88,
    )
    result = validate_lesson_output(lesson)
    assert result.accepted, result.reasons


@pytest.mark.unit
def test_lesson_output_rejects_pii_unsafe_or_invalid_caps_content() -> None:
    lesson = LessonOutput(
        topic="Unknown topic",
        grade=4,
        subject="Mathematics",
        caps_reference="unknown",
        objectives=["Learn"],
        explanation="Email learner@example.com for unsafe weapon details.",
        worked_examples=[],
        practice_questions=["Question?"],
        answer_key=[],
        remediation_hints=[],
        difficulty="core",
        language_level="intermediate",
        safety_classification="unsafe",
        alignment_confidence=0.2,
        quality_score=0.2,
    )
    result = validate_lesson_output(lesson)
    assert not result.accepted
    assert "CAPS alignment invalid" in result.reasons
    assert "unsafe content" in result.reasons
    assert "PII detected" in result.reasons
    assert "answer key missing or inconsistent" in result.reasons


@pytest.mark.unit
def test_arithmetic_validator_and_caps_map_shape() -> None:
    assert arithmetic_expression_is_correct("2 + 3 * 4", "14")
    assert not arithmetic_expression_is_correct("2 + 3 * 4", "20")
    for topic in CAPS_TOPIC_MAP:
        assert {"phase", "grade", "subject", "term", "topic", "subtopic", "prerequisites", "assessment_standards"}.issubset(topic)


@pytest.mark.unit
def test_golden_prompt_coverage_fixture_has_languages_variants_and_topics() -> None:
    fixture = json.loads((REPO_ROOT / "tests" / "fixtures" / "ai" / "golden_prompt_coverage.json").read_text(encoding="utf-8"))
    assert {"English", "isiZulu", "Afrikaans", "isiXhosa"}.issubset(set(fixture["languages"]))
    assert {"standard", "visual", "story_based", "step_by_step", "exam_style", "real_world_sa"}.issubset(set(fixture["variants"]))
    assert fixture["grades"]
    assert fixture["subjects"]
    assert fixture["launch_topics"]


@pytest.mark.unit
def test_makefile_exposes_ai_llm_safety_caps_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "ai-llm-safety-caps-production-readiness-check:" in text
    assert "scripts/check_ai_llm_safety_caps_production_readiness.py" in text
