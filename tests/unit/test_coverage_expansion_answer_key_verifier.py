"""
Unit tests for app.modules.lessons.answer_key_verifier module.
Covers VerificationResult, QuestionVerification, _strip_answers_from_questions,
_normalise_answer, _answers_agree, and AnswerKeyVerifier pure logic.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from app.modules.lessons.answer_key_verifier import (
    AnswerKeyVerifier,
    QuestionVerification,
    VerificationResult,
    _answers_agree,
    _normalise_answer,
    _strip_answers_from_questions,
)


class TestQuestionVerification:
    def test_default_optional_fields(self):
        qv = QuestionVerification(
            question_id="q1",
            derived_answer="42",
            working="Step 1: ...",
            confidence=0.95,
        )
        assert qv.agrees_with_key is None
        assert qv.original_answer is None

    def test_full_init(self):
        qv = QuestionVerification(
            question_id="q1",
            derived_answer="3",
            working="Divide 12 by 4",
            confidence=0.99,
            agrees_with_key=True,
            original_answer="3",
        )
        assert qv.agrees_with_key is True
        assert qv.original_answer == "3"


class TestVerificationResult:
    def test_to_dict_all_agree(self):
        res = VerificationResult(lesson_id="L1", all_agree=True)
        d = res.to_dict()
        assert d["lesson_id"] == "L1"
        assert d["all_agree"] is True
        assert d["verifications"] == []
        assert d["disagreements"] == []
        assert "prompt_template_version" in d

    def test_to_dict_with_verifications(self):
        qv = QuestionVerification(
            question_id="q1",
            derived_answer="3",
            working="12/4=3",
            confidence=0.98,
            agrees_with_key=True,
            original_answer="3",
        )
        res = VerificationResult(
            lesson_id="L2",
            all_agree=True,
            verifications=[qv],
            verification_model="claude-3",
            verification_provider="anthropic",
        )
        d = res.to_dict()
        assert len(d["verifications"]) == 1
        assert d["verifications"][0]["question_id"] == "q1"
        assert d["verification_model"] == "claude-3"


class TestStripAnswersFromQuestions:
    def test_removes_correct_answer_field(self):
        questions = [
            {"id": "q1", "text": "What is 1+1?", "correct_answer": "2", "options": [{"text": "2", "is_correct": True}]},
        ]
        stripped = _strip_answers_from_questions(questions)
        assert "correct_answer" not in stripped[0]

    def test_removes_answer_field(self):
        questions = [{"id": "q1", "text": "What is 1+1?", "answer": "2"}]
        stripped = _strip_answers_from_questions(questions)
        assert "answer" not in stripped[0]

    def test_strips_is_correct_from_options(self):
        questions = [
            {
                "id": "q1",
                "text": "What is 2+2?",
                "options": [
                    {"text": "3", "is_correct": False},
                    {"text": "4", "is_correct": True},
                ],
            }
        ]
        stripped = _strip_answers_from_questions(questions)
        for opt in stripped[0]["options"]:
            assert "is_correct" not in opt

    def test_preserves_non_answer_fields(self):
        questions = [{"id": "q1", "text": "Test?", "difficulty": "easy"}]
        stripped = _strip_answers_from_questions(questions)
        assert stripped[0]["text"] == "Test?"
        assert stripped[0]["difficulty"] == "easy"

    def test_empty_list(self):
        assert _strip_answers_from_questions([]) == []


class TestNormaliseAnswer:
    def test_strips_whitespace_and_lowercases(self):
        assert _normalise_answer("  FOUR  ") == "four"

    def test_decimal_as_integer(self):
        assert _normalise_answer("4.0") == "4"

    def test_sa_comma_decimal(self):
        # Comma-separated decimal normalised to period
        assert _normalise_answer("3,5") == "3.5"

    def test_non_numeric_string(self):
        result = _normalise_answer("fraction")
        assert result == "fraction"

    def test_float_preserved_when_not_integer(self):
        result = _normalise_answer("3.14")
        assert "3.14" in result


class TestAnswersAgree:
    def test_exact_match(self):
        assert _answers_agree("3", "3") is True

    def test_case_insensitive(self):
        assert _answers_agree("Four", "four") is True

    def test_decimal_vs_integer(self):
        assert _answers_agree("4.0", "4") is True

    def test_sa_comma(self):
        assert _answers_agree("3,5", "3.5") is True

    def test_mismatch(self):
        assert _answers_agree("3", "4") is False

    def test_empty_vs_empty(self):
        assert _answers_agree("", "") is True


class TestAnswerKeyVerifierInit:
    def test_init_stores_gateway(self):
        gateway = MagicMock()
        verifier = AnswerKeyVerifier(llm_gateway=gateway)
        assert verifier._gateway is gateway
