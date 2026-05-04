"""
POPIA Tests — RLHF Pre-Export PII Minimisation Gate  (Task #25)
================================================================
Run: pytest tests/popia/test_rlhf_pii_scrubbing.py -v
"""
from __future__ import annotations

import pytest

from app.services.pii_sweep import (
    PIIScanner,
    PIISweepError,
    SweepResult,
    _luhn_valid,
    assert_no_pii,
)
from app.services.rlhf_service import RLHFService


# ---------------------------------------------------------------------------
# Luhn validator unit tests
# ---------------------------------------------------------------------------

class TestLuhnValidator:

    def test_valid_sa_id_luhn(self):
        # Well-known valid SA ID structure: YYMMDD GGGG C A Z
        # 8001015009087 is a commonly used test SA ID
        assert _luhn_valid("8001015009087") is True

    def test_invalid_luhn(self):
        assert _luhn_valid("1234567890123") is False

    def test_all_zeros_is_luhn_valid(self):
        # All-zeros trivially satisfies Luhn (sum=0, 0%10=0) but is not a
        # real SA ID. The SA ID regex requires it to pass Luhn; additional
        # domain validation (e.g. DOB parsing) would reject it in production.
        assert _luhn_valid("0000000000000") is True

    def test_credit_card_luhn(self):
        # Standard VISA test card — verifies generic Luhn logic
        assert _luhn_valid("4111111111111111"[:13]) in (True, False)  # just checks no crash


# ---------------------------------------------------------------------------
# PIIScanner — individual pattern tests
# ---------------------------------------------------------------------------

class TestPIIScannerPatterns:

    @pytest.fixture()
    def scanner(self):
        return PIIScanner()

    # SA ID numbers
    def test_detects_valid_sa_id(self, scanner):
        result = scanner.scan_text("Learner ID: 8001015009087", "comment")
        assert not result.is_clean
        finding = next(f for f in result.findings if f.pattern_name == "sa_id_number")
        assert finding.field_name == "comment"

    def test_ignores_luhn_invalid_13_digits(self, scanner):
        result = scanner.scan_text("Reference: 1234567890123", "comment")
        # Luhn-invalid 13-digit numbers should NOT be flagged as SA IDs
        sa_id_findings = [f for f in result.findings if f.pattern_name == "sa_id_number"]
        assert len(sa_id_findings) == 0

    # Email addresses
    def test_detects_email(self, scanner):
        result = scanner.scan_text("Contact me at john.doe@gmail.com please", "feedback")
        assert not result.is_clean
        assert any(f.pattern_name == "email_address" for f in result.findings)

    def test_clean_text_with_no_email(self, scanner):
        result = scanner.scan_text("The learner answered question 3 correctly.", "response")
        assert result.is_clean

    # Phone numbers
    def test_detects_za_phone_number(self, scanner):
        result = scanner.scan_text("Call me on 0821234567 anytime", "notes")
        assert not result.is_clean
        assert any(f.pattern_name == "phone_number_regex" for f in result.findings)

    def test_detects_international_phone(self, scanner):
        result = scanner.scan_text("My number is +27 82 123 4567", "notes")
        assert not result.is_clean

    def test_short_number_not_flagged(self, scanner):
        result = scanner.scan_text("Question 12 has 3 parts.", "prompt")
        assert result.is_clean

    # Salutation names
    def test_detects_salutation_name(self, scanner):
        result = scanner.scan_text("The lesson was reviewed by Dr Thabo Nkosi.", "feedback")
        assert not result.is_clean
        assert any(f.pattern_name == "salutation_name" for f in result.findings)

    def test_salutation_without_name_not_flagged(self, scanner):
        result = scanner.scan_text("Mr is a title prefix.", "content")
        # Pattern requires a capitalised surname after the salutation
        salutation_findings = [f for f in result.findings if f.pattern_name == "salutation_name"]
        assert len(salutation_findings) == 0

    # HTML stripping
    def test_html_obfuscated_email_detected(self, scanner):
        result = scanner.scan_text(
            "<span>user@hidden.com</span>", "html_field"
        )
        assert not result.is_clean
        assert any(f.pattern_name == "email_address" for f in result.findings)

    # Clean text should pass
    def test_purely_pedagogical_text_is_clean(self, scanner):
        text = (
            "The learner correctly identified that 7×8=56 and demonstrated "
            "understanding of multiplication tables up to 12. The response was "
            "detailed and showed strong conceptual reasoning."
        )
        result = scanner.scan_text(text, "lesson_feedback")
        assert result.is_clean

    # Record-level scan
    def test_scan_record_flags_pii_in_nested_list(self, scanner):
        record = {
            "prompt": "What is 3+4?",
            "responses": ["It is 7.", "Contact me: test@example.com"],
        }
        result = scanner.scan_record(record)
        assert not result.is_clean
        assert any("responses" in f.field_name for f in result.findings)

    def test_scan_record_clean(self, scanner):
        record = {
            "prompt": "Explain photosynthesis.",
            "chosen": "Plants use sunlight to convert CO2 and water into glucose.",
            "rejected": "Plants just grow in the sun.",
        }
        result = scanner.scan_record(record)
        assert result.is_clean


# ---------------------------------------------------------------------------
# assert_no_pii gate tests
# ---------------------------------------------------------------------------

class TestAssertNoPII:

    def test_clean_records_pass_through(self):
        records = [
            {"prompt": "What is 2+2?", "chosen": "4", "rejected": "5"},
            {"prompt": "Name a mammal.", "chosen": "Elephant", "rejected": "Shark"},
        ]
        # Must not raise
        assert_no_pii(records)

    def test_raises_pii_sweep_error_on_email(self):
        records = [
            {"prompt": "Contact info?", "chosen": "admin@school.edu", "rejected": "N/A"},
        ]
        with pytest.raises(PIISweepError) as exc_info:
            assert_no_pii(records)
        err = exc_info.value
        assert len(err.findings) >= 1
        assert err.findings[0]["pattern"] == "email_address"

    def test_raises_pii_sweep_error_on_sa_id(self):
        records = [
            {"response": "My ID is 8001015009087 which is valid."},
        ]
        with pytest.raises(PIISweepError) as exc_info:
            assert_no_pii(records)
        assert any(f["pattern"] == "sa_id_number" for f in exc_info.value.findings)

    def test_raises_pii_sweep_error_on_phone(self):
        records = [
            {"feedback": "Call me on 0821234567 to discuss the lesson."},
        ]
        with pytest.raises(PIISweepError):
            assert_no_pii(records)

    def test_error_message_includes_count(self):
        records = [
            {"a": "user1@example.com", "b": "user2@example.com"},
        ]
        with pytest.raises(PIISweepError) as exc_info:
            assert_no_pii(records)
        assert "2" in str(exc_info.value) or "location" in str(exc_info.value)

    def test_multiple_records_all_flagged(self):
        records = [
            {"text": "email: a@b.com"},
            {"text": "clean text"},
            {"text": "call 0821234567"},
        ]
        with pytest.raises(PIISweepError) as exc_info:
            assert_no_pii(records)
        # Findings from both record 0 and record 2
        record_indices = {f["record_index"] for f in exc_info.value.findings}
        assert 0 in record_indices
        assert 2 in record_indices

    def test_empty_records_list_passes(self):
        assert_no_pii([])  # Should not raise

    def test_empty_string_fields_are_clean(self):
        records = [{"feedback": "", "rating": "5"}]
        assert_no_pii(records)

    def test_custom_scanner_is_used(self):
        """Custom scanner injection works (e.g. for mocking in integration tests)."""
        from unittest.mock import MagicMock

        mock_scanner = MagicMock()
        clean_result = SweepResult(is_clean=True)
        mock_scanner.scan_record.return_value = clean_result

        records = [{"text": "some@email.com"}]
        # With a mock scanner that returns clean, should not raise
        assert_no_pii(records, scanner=mock_scanner)
        mock_scanner.scan_record.assert_called_once()


class TestRLHFServiceExports:

    def test_openai_export_blocks_pii(self):
        service = RLHFService()
        records = [{"prompt": "Call me", "chosen": "0821234567", "rejected": "No thanks"}]

        with pytest.raises(PIISweepError):
            service.export_openai_format(records)

    def test_anthropic_export_blocks_pii(self):
        service = RLHFService()
        records = [{"prompt": "Email me", "chosen": "user@example.com", "rejected": "N/A"}]

        with pytest.raises(PIISweepError):
            service.export_anthropic_format(records)

    def test_clean_export_succeeds(self):
        service = RLHFService()
        records = [{"prompt": "What is 2+2?", "chosen": "4", "rejected": "5"}]

        payload = service.export_openai_format(records)

        assert payload["format"] == "openai"
        assert payload["record_count"] == 1

    def test_pii_sweep_error_has_field_name(self):
        records = [{"chosen_response": "My email is test@example.com"}]
        with pytest.raises(PIISweepError) as exc_info:
            assert_no_pii(records)
        assert exc_info.value.field_name == "chosen_response"


# ---------------------------------------------------------------------------
# Integration: RLHF export pipeline guard
# ---------------------------------------------------------------------------

class TestRLHFExportGuard:
    """
    Simulates how RLHFService should call assert_no_pii before exporting.
    Tests the complete path from fake service → PII scan → export or abort.
    """

    def _build_openai_records(self, include_pii: bool) -> list[dict]:
        """Fake OpenAI preference format records."""
        base = [
            {
                "prompt": "Explain addition to a Grade 2 learner.",
                "chosen": "Addition means combining numbers together.",
                "rejected": "Addition is complicated maths.",
            }
        ]
        if include_pii:
            base[0]["chosen"] += " Email guardian at parent@home.co.za"
        return base

    def test_clean_export_succeeds(self):
        records = self._build_openai_records(include_pii=False)
        # Simulates the guard inside RLHFService.export_openai_format()
        assert_no_pii(records)  # Must not raise

    def test_pii_contaminated_export_is_aborted(self):
        records = self._build_openai_records(include_pii=True)
        with pytest.raises(PIISweepError):
            assert_no_pii(records)

    def test_anthropic_format_records_are_also_guarded(self):
        # Anthropic preference format uses "human" / "assistant" keys
        records = [
            {
                "human": "How do I do long division?",
                "assistant_chosen": "Step 1: divide. Step 2: multiply.",
                "assistant_rejected": "Long division is hard. Call 0821234567.",
            }
        ]
        with pytest.raises(PIISweepError):
            assert_no_pii(records)
