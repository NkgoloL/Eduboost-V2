"""Unit tests for Runtime PII Sanitizer (TSR-8)."""
from __future__ import annotations

import pytest
from app.core.pii_sanitizer import sanitize_payload, SENSITIVE_PII_KEYS


@pytest.mark.unit
def test_sensitive_pii_keys_are_pseudonymized():
    dirty_payload = {
        "event_type": "parent_consent_submitted",
        "email": "guardian.test@example.com",
        "name": "Jane Doe",
        "sa_id_number": "8501015009087",
        "phone": "+27821234567",
        "learner_id": "learner-uuid-1234",
        "metadata": {
            "dob": "2012-05-14",
            "physical_address": "123 Education Way, Cape Town",
            "grade": 5,
        },
    }

    cleaned = sanitize_payload(dirty_payload)

    # Asserts on top-level sensitive fields
    assert cleaned["email"].startswith("pseudonym_")
    assert cleaned["email"] != "guardian.test@example.com"
    assert cleaned["name"].startswith("pseudonym_")
    assert cleaned["name"] != "Jane Doe"
    assert cleaned["sa_id_number"].startswith("pseudonym_")
    assert cleaned["sa_id_number"] != "8501015009087"
    assert cleaned["phone"].startswith("pseudonym_")

    # Non-sensitive keys remain intact
    assert cleaned["event_type"] == "parent_consent_submitted"
    assert cleaned["learner_id"] == "learner-uuid-1234"

    # Nested dictionary sanitization
    assert cleaned["metadata"]["dob"].startswith("pseudonym_")
    assert cleaned["metadata"]["physical_address"].startswith("pseudonym_")
    assert cleaned["metadata"]["grade"] == 5


@pytest.mark.unit
def test_inline_pii_redaction_in_text():
    dirty_text = "User email is teacher@school.za with ID 9901015009087 and call +27839876543."
    cleaned = sanitize_payload(dirty_text)

    assert "[REDACTED_EMAIL]" in cleaned
    assert "teacher@school.za" not in cleaned
    assert "[REDACTED_ID]" in cleaned
    assert "9901015009087" not in cleaned
    assert "[REDACTED_PHONE]" in cleaned
    assert "+27839876543" not in cleaned


@pytest.mark.unit
def test_safe_structures_preserve_types():
    clean_dict = {
        "score": 0.85,
        "items": [1, 2, 3],
        "tags": ("math", "fractions"),
        "is_active": True,
    }
    result = sanitize_payload(clean_dict)
    assert result == clean_dict
