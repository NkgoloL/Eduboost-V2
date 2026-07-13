from __future__ import annotations

import pytest

from app.services.pii_sweep import PIIScanner, PIISweepError, assert_no_pii


def test_pii_scanner_detects_email_phone_html_and_names_without_mutating_safe_text() -> None:
    scanner = PIIScanner()

    safe = scanner.scan_text("Learner solved the fraction problem using visual models.", "feedback")
    unsafe = scanner.scan_record(
        {
            "prompt": "<script>alert('x')</script> Contact Dr Molefe at learner@example.com",
            "responses": [
                "Please call 071 234 5678 after school.",
                "No personal data here.",
            ],
        }
    )

    assert safe.is_clean is True
    assert unsafe.is_clean is False
    assert {finding.pattern_name for finding in unsafe.findings} >= {
        "email_address",
        "phone_number_regex",
        "salutation_name",
    }
    assert {finding.field_name for finding in unsafe.findings} >= {"prompt", "responses[0]"}


def test_assert_no_pii_allows_clean_exports_and_fails_closed_with_field_inventory() -> None:
    clean_records = [
        {"chosen": "Explain place value using blocks.", "rejected": "Use a less clear example."},
        {"chosen": "Try another fraction model.", "metadata": ["grade 4", "mathematics"]},
    ]
    unsafe_records = [
        {"chosen": "Email learner@example.com for the answer.", "rejected": "No"},
        {"chosen": "Safe text", "rejected": "Phone 082 123 4567"},
    ]

    assert_no_pii(clean_records)

    with pytest.raises(PIISweepError) as excinfo:
        assert_no_pii(unsafe_records)

    error = excinfo.value
    assert error.field_name == "chosen"
    assert "Export aborted" in str(error)
    assert {finding["record_index"] for finding in error.findings} == {0, 1}
    assert {finding["field"] for finding in error.findings} == {"chosen", "rejected"}
