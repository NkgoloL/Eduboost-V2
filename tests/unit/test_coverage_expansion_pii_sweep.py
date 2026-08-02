"""
Unit tests for app.services.pii_sweep to cover scanner layers, Luhn validation,
salutation patterns, email/phone patterns, record sweeps, and PIISweepError guards.
"""
from __future__ import annotations

import pytest
from app.services.pii_sweep import (
    PIIScanner,
    PIISweepError,
    PIIFinding,
    SweepResult,
    _luhn_valid,
    assert_no_pii,
)


def test_luhn_valid():
    # Valid SA ID example (passes Luhn)
    assert _luhn_valid("8001015009087") is True
    # Invalid SA ID
    assert _luhn_valid("8001015009088") is False


def test_pii_scanner_clean_text():
    scanner = PIIScanner()
    result = scanner.scan_text("This is clean educational content with no PII.")
    assert result.is_clean is True
    assert len(result.findings) == 0


def test_pii_scanner_non_string_or_empty():
    scanner = PIIScanner()
    assert scanner.scan_text("").is_clean is True
    assert scanner.scan_text(None).is_clean is True  # type: ignore


def test_pii_scanner_email():
    scanner = PIIScanner()
    result = scanner.scan_text("Contact user@example.com for help.", field_name="comment")
    assert result.is_clean is False
    assert len(result.findings) >= 1
    assert any(f.pattern_name == "email_address" for f in result.findings)


def test_pii_scanner_phone():
    scanner = PIIScanner()
    result = scanner.scan_text("Call +27 82 123 4567 today.", field_name="phone_field")
    assert result.is_clean is False
    assert any("phone_number" in f.pattern_name for f in result.findings)


def test_pii_scanner_salutation():
    scanner = PIIScanner()
    result = scanner.scan_text("Thanks to Dr John Smith for reviewing.", field_name="feedback")
    assert result.is_clean is False
    assert any(f.pattern_name == "salutation_name" for f in result.findings)


def test_pii_scanner_sa_id():
    scanner = PIIScanner()
    # Using a valid Luhn 13-digit number
    result = scanner.scan_text("My ID is 8001015009087.", field_name="id_field")
    assert result.is_clean is False
    assert any(f.pattern_name == "sa_id_number" for f in result.findings)


def test_pii_scanner_scan_record_with_lists():
    scanner = PIIScanner()
    record = {
        "title": "Clean Lesson",
        "comments": ["Looks good", "Email me at test@example.com"],
        "metadata": {"other": 123},
    }
    result = scanner.scan_record(record)
    assert result.is_clean is False
    assert any(f.field_name == "comments[1]" for f in result.findings)


def test_assert_no_pii_clean():
    records = [{"content": "Safe content 1"}, {"content": "Safe content 2"}]
    # Should not raise
    assert_no_pii(records)


def test_assert_no_pii_error():
    records = [
        {"content": "Safe content"},
        {"content": "Contact Mr John Doe immediately"},
    ]
    with pytest.raises(PIISweepError) as exc_info:
        assert_no_pii(records)

    err = exc_info.value
    assert "PII detected" in str(err)
    assert len(err.findings) >= 1
    assert err.field_name == "content"
