"""
Phase 1 — EC-05: PII and unsafe-content filter tests.
Every test must verify both the pass and fail paths.
"""
from __future__ import annotations

import pytest

from app.services.safety_filter import (
    SafetyFilter,
    ViolationCategory,
)


@pytest.fixture()
def sf() -> SafetyFilter:
    return SafetyFilter()


# ---------------------------------------------------------------------------
# Clean content — must pass
# ---------------------------------------------------------------------------


class TestCleanContent:
    def test_plain_educational_text_passes(self, sf):
        text = (
            "When multiplying 4 × 3, we add 4 to itself 3 times: "
            "4 + 4 + 4 = 12. This is the foundation of multiplication."
        )
        result = sf.check_text(text, context="test")
        assert result.passed is True
        assert result.violations == []

    def test_maths_problem_with_numbers_passes(self, sf):
        # Ensure ordinary number sequences don't trigger SA ID false-positive
        text = "Calculate: 234 + 567 = 801. Check: 801 - 567 = 234."
        result = sf.check_text(text, context="test")
        assert result.passed is True

    def test_empty_string_passes(self, sf):
        result = sf.check_text("", context="test")
        assert result.passed is True

    def test_json_payload_without_pii_passes(self, sf):
        import json
        payload = json.dumps({
            "question": "How many legs does a spider have?",
            "options": ["6", "8", "10", "12"],
            "correct_answer_index": 1,
        })
        result = sf.check_text(payload, context="llm_output")
        assert result.passed is True


# ---------------------------------------------------------------------------
# PII detection — must fail
# ---------------------------------------------------------------------------


class TestPIIDetection:
    def test_sa_id_number_detected(self, sf):
        text = "Learner ID: 9001015800082"
        result = sf.check_text(text, context="test")
        assert result.passed is False
        cats = result.violation_categories
        assert ViolationCategory.PII_SA_ID.value in cats

    def test_sa_id_number_in_json_detected(self, sf):
        text = '{"learner_id": "8507125800086", "name": "test"}'
        result = sf.check_text(text, context="llm_output")
        assert result.passed is False
        assert ViolationCategory.PII_SA_ID.value in result.violation_categories

    def test_email_address_detected(self, sf):
        text = "Contact teacher at teacher@school.co.za for more info."
        result = sf.check_text(text, context="test")
        assert result.passed is False
        assert ViolationCategory.PII_EMAIL.value in result.violation_categories

    def test_sa_phone_number_detected_with_prefix(self, sf):
        text = "Call the school at +27 82 123 4567."
        result = sf.check_text(text, context="test")
        assert result.passed is False
        assert ViolationCategory.PII_PHONE.value in result.violation_categories

    def test_sa_phone_number_detected_local_format(self, sf):
        text = "The number is 083 456 7890."
        result = sf.check_text(text, context="test")
        assert result.passed is False
        assert ViolationCategory.PII_PHONE.value in result.violation_categories

    def test_bank_account_detected_with_context_word(self, sf):
        text = "Account: 1234567890"
        result = sf.check_text(text, context="test")
        assert result.passed is False
        assert ViolationCategory.PII_BANK_ACCOUNT.value in result.violation_categories

    def test_twelve_digit_number_not_flagged_as_id(self, sf):
        # SA ID is exactly 13 digits; 12 should not trigger
        text = "Reference: 123456789012"
        result = sf.check_text(text, context="test")
        # 12 digits should not match the 13-digit SA ID pattern
        id_violations = [
            v for v in result.violations
            if v.category == ViolationCategory.PII_SA_ID
        ]
        assert len(id_violations) == 0


# ---------------------------------------------------------------------------
# Unsafe content — must fail
# ---------------------------------------------------------------------------


class TestUnsafeContent:
    def test_violence_keyword_detected(self, sf):
        text = "The soldier murdered the prisoner during the battle."
        result = sf.check_text(text, context="llm_output")
        assert result.passed is False
        assert ViolationCategory.UNSAFE_VIOLENCE.value in result.violation_categories

    def test_adult_content_keyword_detected(self, sf):
        text = "The biology lesson covers sexual reproduction in plants."
        result = sf.check_text(text, context="llm_output")
        assert result.passed is False
        assert ViolationCategory.UNSAFE_ADULT.value in result.violation_categories

    def test_self_harm_phrase_detected(self, sf):
        text = "He talked about suicide as a way out."
        result = sf.check_text(text, context="llm_output")
        assert result.passed is False
        assert ViolationCategory.UNSAFE_SELF_HARM.value in result.violation_categories

    def test_hate_speech_detected(self, sf):
        text = "Using the word kaffir is deeply offensive."
        result = sf.check_text(text, context="llm_output")
        assert result.passed is False
        assert ViolationCategory.UNSAFE_HATE.value in result.violation_categories


# ---------------------------------------------------------------------------
# Source bundle check
# ---------------------------------------------------------------------------


class TestSourceBundleCheck:
    def test_clean_sources_pass(self, sf):
        sources = [
            {
                "source_document_id": "doc-001",
                "source_title": "Grade 4 Maths Textbook",
                "text": "Multiplication is repeated addition. 4 × 3 = 12.",
            }
        ]
        result = sf.check_source_bundle(sources, context="etl_source")
        assert result.passed is True

    def test_pii_in_source_text_detected(self, sf):
        sources = [
            {
                "source_document_id": "doc-002",
                "source_title": "Sample Paper",
                "text": "Learner John's ID is 9001015800082 and he scored 80%.",
            }
        ]
        result = sf.check_source_bundle(sources, context="etl_source")
        assert result.passed is False
        assert ViolationCategory.PII_SA_ID.value in result.violation_categories

    def test_pii_in_source_title_detected(self, sf):
        sources = [
            {
                "source_document_id": "doc-003",
                "source_title": "Document from teacher@school.co.za",
                "text": "Clean educational content about fractions.",
            }
        ]
        result = sf.check_source_bundle(sources, context="etl_source")
        assert result.passed is False

    def test_empty_sources_pass(self, sf):
        result = sf.check_source_bundle([], context="etl_source")
        assert result.passed is True

    def test_multiple_violations_aggregated(self, sf):
        sources = [
            {
                "source_document_id": "doc-004",
                "text": "Contact: teacher@school.co.za, ID: 8507125800086",
            }
        ]
        result = sf.check_source_bundle(sources)
        assert result.passed is False
        cats = set(result.violation_categories)
        assert ViolationCategory.PII_EMAIL.value in cats
        assert ViolationCategory.PII_SA_ID.value in cats


# ---------------------------------------------------------------------------
# SafetyCheckResult helpers
# ---------------------------------------------------------------------------


class TestSafetyCheckResult:
    def test_summary_pass(self, sf):
        result = sf.check_text("Clean content about numbers.", context="test")
        assert result.summary == "pass"

    def test_summary_fail_includes_categories(self, sf):
        result = sf.check_text(
            "Contact us at test@example.com", context="test"
        )
        assert result.summary.startswith("fail:")
        assert "pii_email" in result.summary

    def test_redacted_excerpt_does_not_expose_full_match(self, sf):
        text = "ID number: 8507125800086"
        result = sf.check_text(text, context="test")
        for v in result.violations:
            if v.category == ViolationCategory.PII_SA_ID:
                # Redacted excerpt must be shorter or masked
                assert "*" in v.redacted_excerpt or len(v.redacted_excerpt) < 13
