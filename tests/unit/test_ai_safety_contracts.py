from __future__ import annotations

import json

from app.core.llm_gateway import ExecutiveService
from app.domain.llm_schemas import DiagnosticItemContract, LessonContent
from app.services.ai_safety import redact_pii_text, score_lesson_quality


def test_lesson_content_enforces_caps_reference_prefix() -> None:
    lesson = LessonContent(
        title="Fractions",
        introduction="Intro",
        main_content="Fractions are equal parts.",
        worked_example="Two quarters are one half.",
        practice_question="What is 1/2?",
        answer="One half",
        cultural_hook="Use rands at a spaza shop.",
        caps_reference="CAPS:caps-mvp-2026.05:G4:mathematics:T1:fractions:equivalent-fractions",
    )
    assert lesson.trust_label.caps_linked is True
    assert lesson.trust_label.answer_checked is True


def test_diagnostic_item_contract_validates_caps_reference_and_options() -> None:
    item = DiagnosticItemContract(
        item_id="item-1",
        subject="mathematics",
        grade=4,
        topic="fractions",
        skill="equivalent fractions",
        difficulty=0.2,
        discrimination=1.1,
        correct_answer="B",
        distractors={"A": "1/4", "B": "2/4", "C": "3/4", "D": "4/4"},
        explanation="2/4 is equivalent to 1/2.",
        caps_reference="CAPS:caps-mvp-2026.05:G4:mathematics:T1:fractions:equivalent-fractions",
    )
    assert item.correct_answer == "B"


def test_pii_redaction_removes_email_phone_and_id_numbers() -> None:
    raw = "Learner Jane: jane@example.com, 082 123 4567, 0101015009087"
    redacted = redact_pii_text(raw)
    assert "jane@example.com" not in redacted
    assert "082" not in redacted
    assert "0101015009087" not in redacted


def test_quality_score_rewards_caps_answer_and_pedagogy() -> None:
    score = score_lesson_quality(
        content="Fractions lesson with rands. " * 20,
        caps_aligned=True,
        answer_present=True,
        has_worked_example=True,
        has_practice=True,
    )
    assert score.overall >= 0.8


def test_mock_llm_provider_is_deterministic() -> None:
    service = ExecutiveService()
    first = json.loads(service._call_mock("Grade 4 | Subject: Mathematics | Topic: Fractions", operation="lesson_generation"))
    second = json.loads(service._call_mock("Grade 4 | Subject: Mathematics | Topic: Fractions", operation="lesson_generation"))
    assert first == second
    assert first["safety_classification"] == "safe"
