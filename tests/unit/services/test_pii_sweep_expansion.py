"""Batch 197: Unit tests for pii_sweep service."""
import pytest

from app.services.pii_sweep import (
    PIIFinding,
    PIIScanner,
    PIISweepError,
    SweepResult,
    assert_no_pii,
    _luhn_valid,
)


# ─────────────────────────────────────────────
# Luhn validation helper
# ─────────────────────────────────────────────


class TestLuhnValid:
    def test_valid_luhn_number(self):
        # 4532015112830366 is a well-known test Luhn-valid number
        assert _luhn_valid("4532015112830366") is True

    def test_invalid_luhn_number(self):
        assert _luhn_valid("1234567890123456") is False

    def test_single_zero(self):
        assert _luhn_valid("0") is True


# ─────────────────────────────────────────────
# SweepResult
# ─────────────────────────────────────────────


class TestSweepResult:
    def test_initially_clean(self):
        result = SweepResult(is_clean=True)
        assert result.is_clean is True
        assert result.findings == []

    def test_add_finding_marks_dirty(self):
        result = SweepResult(is_clean=True)
        finding = PIIFinding(pattern_name="email_address", matched_value="[REDACTED]", field_name="text")
        result.add(finding)
        assert result.is_clean is False
        assert len(result.findings) == 1

    def test_add_multiple_findings(self):
        result = SweepResult(is_clean=True)
        for i in range(3):
            result.add(PIIFinding("email_address", "[R]", f"field_{i}"))
        assert len(result.findings) == 3
        assert result.is_clean is False


# ─────────────────────────────────────────────
# PIIFinding
# ─────────────────────────────────────────────


class TestPIIFinding:
    def test_fields(self):
        f = PIIFinding(pattern_name="sa_id_number", matched_value="900**", field_name="id_field", position=10)
        assert f.pattern_name == "sa_id_number"
        assert f.field_name == "id_field"
        assert f.position == 10

    def test_default_position(self):
        f = PIIFinding(pattern_name="email_address", matched_value="[R]", field_name="email")
        assert f.position == 0


# ─────────────────────────────────────────────
# PIIScanner.scan_text
# ─────────────────────────────────────────────


class TestPIIScannerScanText:
    def _scanner(self):
        return PIIScanner()

    def test_clean_text_is_clean(self):
        result = self._scanner().scan_text("The quick brown fox jumps over the lazy dog.")
        assert result.is_clean is True

    def test_empty_string_is_clean(self):
        result = self._scanner().scan_text("")
        assert result.is_clean is True

    def test_whitespace_only_is_clean(self):
        result = self._scanner().scan_text("   ")
        assert result.is_clean is True

    def test_email_detected(self):
        result = self._scanner().scan_text("Contact me at user@example.com for details.")
        assert result.is_clean is False
        assert any(f.pattern_name == "email_address" for f in result.findings)

    def test_salutation_detected(self):
        result = self._scanner().scan_text("Please contact Mr. John Smith about this.")
        assert result.is_clean is False
        assert any(f.pattern_name == "salutation_name" for f in result.findings)

    def test_phone_number_detected(self):
        result = self._scanner().scan_text("Call me on +27 82 123 4567 for help.")
        assert result.is_clean is False
        assert any("phone" in f.pattern_name for f in result.findings)

    def test_html_stripped_before_scanning(self):
        # Email hidden in an HTML tag should still be detected after stripping
        result = self._scanner().scan_text("<b>user@example.com</b>")
        assert result.is_clean is False

    def test_non_string_returns_clean(self):
        result = self._scanner().scan_text(123)  # type: ignore
        assert result.is_clean is True

    def test_field_name_recorded_on_finding(self):
        result = self._scanner().scan_text("user@example.com", field_name="email_field")
        assert all(f.field_name == "email_field" for f in result.findings)


# ─────────────────────────────────────────────
# PIIScanner.scan_record
# ─────────────────────────────────────────────


class TestPIIScannerScanRecord:
    def _scanner(self):
        return PIIScanner()

    def test_clean_record_is_clean(self):
        record = {"question": "What is 2+2?", "answer": "Four"}
        result = self._scanner().scan_record(record)
        assert result.is_clean is True

    def test_record_with_email_is_dirty(self):
        record = {"question": "Contact user@example.com", "answer": "ok"}
        result = self._scanner().scan_record(record)
        assert result.is_clean is False

    def test_record_with_list_field_scanned(self):
        record = {"choices": ["user@example.com", "clean text"]}
        result = self._scanner().scan_record(record)
        assert result.is_clean is False
        assert any("choices" in f.field_name for f in result.findings)

    def test_record_with_non_string_fields_skipped(self):
        record = {"count": 42, "ratio": 0.95, "tags": None}
        result = self._scanner().scan_record(record)
        assert result.is_clean is True


# ─────────────────────────────────────────────
# assert_no_pii
# ─────────────────────────────────────────────


class TestAssertNoPii:
    def test_clean_records_do_not_raise(self):
        records = [
            {"question": "What is 2+2?", "answer": "Four"},
            {"question": "Name the capital of South Africa.", "answer": "Pretoria"},
        ]
        # Should not raise
        assert_no_pii(records)

    def test_records_with_email_raise_pii_sweep_error(self):
        records = [
            {"question": "What is user@example.com?", "answer": "unknown"},
        ]
        with pytest.raises(PIISweepError) as exc_info:
            assert_no_pii(records)
        assert exc_info.value.findings
        assert "email" in exc_info.value.field_name or len(exc_info.value.findings) > 0

    def test_empty_records_do_not_raise(self):
        assert_no_pii([])

    def test_pii_sweep_error_has_findings_and_field(self):
        records = [{"text": "Please call Mr. John Smith for details."}]
        with pytest.raises(PIISweepError) as exc_info:
            assert_no_pii(records)
        err = exc_info.value
        assert isinstance(err.findings, list)
        assert len(err.findings) > 0
        assert err.field_name != ""

    def test_custom_scanner_used(self):
        """Custom scanner that detects nothing - should not raise."""
        class NullScanner:
            def scan_record(self, record):
                return SweepResult(is_clean=True)

        records = [{"text": "user@example.com"}]
        # Should not raise since our custom scanner returns clean
        assert_no_pii(records, scanner=NullScanner())  # type: ignore

    def test_pii_sweep_error_is_exception_subclass(self):
        err = PIISweepError("test", findings=[], field_name="field")
        assert isinstance(err, Exception)
        assert err.findings == []
        assert err.field_name == "field"
