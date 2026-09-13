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


@pytest.mark.unit
def test_hmac_pseudonymization_with_custom_and_env_salt(monkeypatch: pytest.MonkeyPatch):
    from app.core.pii_sanitizer import hash_pseudonym

    # Same value with different salts produces different pseudonyms (keyed HMAC)
    val = "8501015009087"
    p1 = hash_pseudonym(val, salt="secret_salt_a")
    p2 = hash_pseudonym(val, salt="secret_salt_b")
    p3 = hash_pseudonym(val, salt="secret_salt_a")

    assert p1.startswith("pseudonym_")
    assert p2.startswith("pseudonym_")
    assert p1 != p2
    assert p1 == p3

    # Environment variable salt override
    monkeypatch.setenv("PII_PSEUDONYMIZATION_SALT", "env_secret_salt_123")
    p_env = hash_pseudonym(val)
    p_direct = hash_pseudonym(val, salt="env_secret_salt_123")
    assert p_env == p_direct

