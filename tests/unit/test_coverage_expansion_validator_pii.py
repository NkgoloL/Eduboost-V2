"""
Unit tests for:
  - app.services.content_validator (ContentValidator, ValidationResult)
  - app.services.pii_sweep (PIIScanner, SweepResult, PIISweepError)
"""
from __future__ import annotations

import json
import pytest

from app.services.content_validator import ContentValidator, ValidationResult
from app.services.pii_sweep import (
    PIIScanner,
    PIISweepError,
    SweepResult,
    PIIFinding,
    _luhn_valid,
)


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------

class TestValidationResult:
    def test_error_summary_empty_when_passed(self):
        res = ValidationResult(passed=True, content_type="lesson", schema_version="v1")
        assert res.error_summary == ""

    def test_error_summary_joins_errors(self):
        res = ValidationResult(
            passed=False,
            content_type="lesson",
            schema_version="v1",
            errors=["field1: missing", "field2: invalid"],
        )
        assert "field1" in res.error_summary
        assert "field2" in res.error_summary


# ---------------------------------------------------------------------------
# ContentValidator
# ---------------------------------------------------------------------------

class TestContentValidator:
    def setup_method(self):
        self.validator = ContentValidator()

    def test_unknown_content_type_fails(self):
        result = self.validator.validate("{}", content_type="nonexistent_type")
        assert not result.passed
        assert "Unknown content type" in result.error_summary

    def test_malformed_json_fails(self):
        result = self.validator.validate("{bad json}", content_type="lesson")
        assert not result.passed
        assert "JSON parse error" in result.error_summary

    def test_strips_markdown_fences(self):
        # JSON wrapped in code fence should be stripped and then validated
        result = self.validator.validate("```json\n{bad json}\n```", content_type="lesson")
        assert not result.passed
        # Should get a json parse or schema error, not an "unknown" error
        assert "Unknown content type" not in result.error_summary

    def test_diagnostic_item_not_list_fails(self):
        result = self.validator.validate('{"key": "value"}', content_type="diagnostic_item")
        assert not result.passed
        assert "JSON array" in result.error_summary

    def test_diagnostic_item_empty_array_fails(self):
        result = self.validator.validate("[]", content_type="diagnostic_item")
        assert not result.passed
        assert "empty array" in result.error_summary.lower()


# ---------------------------------------------------------------------------
# PIIScanner — _luhn_valid
# ---------------------------------------------------------------------------

class TestLuhnValid:
    def test_valid_luhn(self):
        # Standard test number that passes Luhn
        assert _luhn_valid("4532015112830366") is True

    def test_invalid_luhn(self):
        assert _luhn_valid("1234567890123") is False

    def test_all_zeros(self):
        # All zeros passes Luhn (total=0)
        assert _luhn_valid("0000000000") is True


# ---------------------------------------------------------------------------
# SweepResult
# ---------------------------------------------------------------------------

class TestSweepResult:
    def test_initially_clean(self):
        result = SweepResult(is_clean=True)
        assert result.is_clean is True
        assert result.findings == []

    def test_add_marks_dirty(self):
        result = SweepResult(is_clean=True)
        finding = PIIFinding(pattern_name="email", matched_value="x@y.com", field_name="text")
        result.add(finding)
        assert not result.is_clean
        assert len(result.findings) == 1


# ---------------------------------------------------------------------------
# PIIScanner
# ---------------------------------------------------------------------------

class TestPIIScanner:
    def setup_method(self):
        self.scanner = PIIScanner()

    def test_clean_text_is_clean(self):
        result = self.scanner.scan_text("The capital of South Africa is Pretoria.", "test_field")
        assert result.is_clean

    def test_detects_email(self):
        result = self.scanner.scan_text("Send to admin@school.co.za today.", "email_field")
        assert not result.is_clean
        categories = [f.pattern_name for f in result.findings]
        assert any("email" in c.lower() for c in categories)

    def test_detects_phone_za(self):
        result = self.scanner.scan_text("Call +27 71 123 4567 for support.", "contact")
        assert not result.is_clean

    def test_detects_salutation_name(self):
        result = self.scanner.scan_text("Mr. John Smith visited the school.", "notes")
        assert not result.is_clean

    def test_empty_string_is_clean(self):
        result = self.scanner.scan_text("", "field")
        assert result.is_clean

    def test_non_string_gracefully_handled(self):
        # scan_text should handle non-str values gracefully
        result = self.scanner.scan_text(None, "field")  # type: ignore[arg-type]
        assert result.is_clean

    def test_scan_record_clean(self):
        record = {"subject": "Mathematics", "topic": "Algebra", "grade": "7"}
        result = self.scanner.scan_record(record)
        assert result.is_clean

    def test_scan_record_dirty(self):
        record = {"subject": "Math", "notes": "Contact mrs@school.za"}
        result = self.scanner.scan_record(record)
        assert not result.is_clean

    def test_scan_record_list_fields(self):
        record = {"tags": ["algebra", "admin@school.za", "grade-7"]}
        result = self.scanner.scan_record(record)
        assert not result.is_clean


class TestPIISweepError:
    def test_stores_findings_and_field(self):
        err = PIISweepError(
            "PII detected",
            findings=[{"pattern": "email", "value": "x@y.com"}],
            field_name="notes",
        )
        assert err.field_name == "notes"
        assert len(err.findings) == 1
        assert str(err) == "PII detected"

    def test_is_exception(self):
        err = PIISweepError("test", findings=[])
        assert isinstance(err, Exception)
