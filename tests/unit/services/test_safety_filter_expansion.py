"""Batch 200: Unit tests for safety_filter service - SafetyFilter, SafetyCheckResult, SafetyViolation."""
import pytest
from app.services.safety_filter import (
    SafetyCheckResult,
    SafetyFilter,
    SafetyViolation,
    ViolationCategory,
    _redact,
)


# ─────────────────────────────────────────────
# _redact helper
# ─────────────────────────────────────────────


class TestRedactHelper:
    def test_short_text_fully_redacted(self):
        assert _redact("abc", keep_chars=4) == "***"

    def test_longer_text_partially_redacted(self):
        result = _redact("user@example.com", keep_chars=4)
        assert result.startswith("user")
        assert "*" in result
        assert "@" not in result[4:]

    def test_exact_keep_chars_length_fully_redacted(self):
        # 4 chars exactly — fully replaced
        result = _redact("abcd", keep_chars=4)
        assert result == "****"


# ─────────────────────────────────────────────
# SafetyCheckResult
# ─────────────────────────────────────────────


class TestSafetyCheckResult:
    def test_passed_result_with_no_violations(self):
        result = SafetyCheckResult(passed=True, context="test")
        assert result.passed is True
        assert result.violations == []
        assert result.violation_categories == []
        assert result.summary == "pass"

    def test_failed_result_summary_contains_categories(self):
        violation = SafetyViolation(
            category=ViolationCategory.PII_EMAIL,
            description="Email found",
        )
        result = SafetyCheckResult(passed=False, context="llm_output", violations=[violation])
        assert result.passed is False
        assert "pii_email_address" in result.summary
        assert result.summary.startswith("fail:")

    def test_violation_categories_list(self):
        violations = [
            SafetyViolation(ViolationCategory.PII_EMAIL, "Email"),
            SafetyViolation(ViolationCategory.UNSAFE_VIOLENCE, "Violence"),
        ]
        result = SafetyCheckResult(passed=False, context="ctx", violations=violations)
        cats = result.violation_categories
        assert "pii_email_address" in cats
        assert "unsafe_violence" in cats


# ─────────────────────────────────────────────
# SafetyFilter.check_text
# ─────────────────────────────────────────────


class TestSafetyFilterCheckText:
    def _filter(self):
        return SafetyFilter()

    def test_clean_text_passes(self):
        result = self._filter().check_text("South Africa has 11 official languages.")
        assert result.passed is True
        assert result.violations == []

    def test_email_detected(self):
        result = self._filter().check_text("Contact support@example.co.za for help.")
        assert result.passed is False
        assert any(v.category == ViolationCategory.PII_EMAIL for v in result.violations)

    def test_phone_number_detected(self):
        result = self._filter().check_text("Call us at +27 82 123 4567 today.")
        assert result.passed is False
        assert any(v.category == ViolationCategory.PII_PHONE for v in result.violations)

    def test_bank_account_detected(self):
        result = self._filter().check_text("Account: 123456789 at your service.")
        assert result.passed is False
        assert any(v.category == ViolationCategory.PII_BANK_ACCOUNT for v in result.violations)

    def test_violence_keyword_detected(self):
        result = self._filter().check_text("The character was killed in the scene.")
        assert result.passed is False
        assert any(v.category == ViolationCategory.UNSAFE_VIOLENCE for v in result.violations)

    def test_adult_keyword_detected(self):
        result = self._filter().check_text("Adult sexual content is blocked here.")
        assert result.passed is False
        assert any(v.category == ViolationCategory.UNSAFE_ADULT for v in result.violations)

    def test_self_harm_keyword_detected(self):
        result = self._filter().check_text("The character thought about suicide.")
        assert result.passed is False
        assert any(v.category == ViolationCategory.UNSAFE_SELF_HARM for v in result.violations)

    def test_hate_keyword_detected(self):
        result = self._filter().check_text("They used the slur in the conversation.")
        assert result.passed is False
        assert any(v.category == ViolationCategory.UNSAFE_HATE for v in result.violations)

    def test_context_recorded_in_result(self):
        result = self._filter().check_text("Clean text", context="etl_source_chunk")
        assert result.context == "etl_source_chunk"

    def test_multiple_violations_collected(self):
        text = "Contact user@example.com and they committed murder."
        result = self._filter().check_text(text)
        assert result.passed is False
        cats = result.violation_categories
        assert "pii_email_address" in cats
        assert "unsafe_violence" in cats


# ─────────────────────────────────────────────
# SafetyFilter.check_source_bundle
# ─────────────────────────────────────────────


class TestSafetyFilterCheckSourceBundle:
    def _filter(self):
        return SafetyFilter()

    def test_clean_bundle_passes(self):
        sources = [
            {"text": "Fractions represent parts of a whole.", "title": "Math Notes"},
            {"text": "The Limpopo province has diverse ecosystems.", "citation_text": "Reference text"},
        ]
        result = self._filter().check_source_bundle(sources)
        assert result.passed is True

    def test_bundle_with_email_in_text_fails(self):
        sources = [{"text": "Please email admin@school.co.za for help."}]
        result = self._filter().check_source_bundle(sources)
        assert result.passed is False
        assert any(v.category == ViolationCategory.PII_EMAIL for v in result.violations)

    def test_bundle_with_violence_in_title_fails(self):
        sources = [{"title": "How people are killed in war", "text": "Clean educational text."}]
        result = self._filter().check_source_bundle(sources)
        assert result.passed is False

    def test_empty_bundle_passes(self):
        result = self._filter().check_source_bundle([])
        assert result.passed is True

    def test_non_string_fields_ignored(self):
        sources = [{"text": None, "title": 42, "extra": ["list"]}]
        result = self._filter().check_source_bundle(sources)
        assert result.passed is True

    def test_bundle_context_recorded(self):
        result = self._filter().check_source_bundle([], context="etl_pipeline")
        assert result.context == "etl_pipeline"


# ─────────────────────────────────────────────
# ViolationCategory enum
# ─────────────────────────────────────────────


class TestViolationCategory:
    def test_all_expected_categories_present(self):
        categories = {v.value for v in ViolationCategory}
        expected = {
            "pii_sa_id_number",
            "pii_phone_number",
            "pii_email_address",
            "pii_bank_account",
            "unsafe_violence",
            "unsafe_adult_content",
            "unsafe_self_harm",
            "unsafe_hate_speech",
        }
        assert expected == categories
