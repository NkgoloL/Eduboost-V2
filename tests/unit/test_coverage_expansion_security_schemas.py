"""
Unit tests for:
  - app.core.security (hash_email, hash_password, verify_password, decode_token)
  - app.services.content_schemas (DiagnosticItemPayload, LessonPayload, get_schema_version)
"""
from __future__ import annotations

import pytest

from app.core.security import hash_email, hash_password, verify_password
from app.services.content_schemas import (
    CONTENT_TYPE_SCHEMA_VERSIONS,
    DiagnosticItemPayload,
    get_schema_version,
)


# ---------------------------------------------------------------------------
# hash_email
# ---------------------------------------------------------------------------

class TestHashEmail:
    def test_returns_64_char_hex(self):
        h = hash_email("test@example.com")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_deterministic(self):
        assert hash_email("user@school.co.za") == hash_email("user@school.co.za")

    def test_case_insensitive(self):
        assert hash_email("User@Example.COM") == hash_email("user@example.com")

    def test_strips_whitespace(self):
        assert hash_email("  test@example.com  ") == hash_email("test@example.com")

    def test_different_emails_differ(self):
        assert hash_email("a@example.com") != hash_email("b@example.com")


# ---------------------------------------------------------------------------
# hash_password / verify_password
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hashed_differs_from_plain(self):
        plain = "SecurePass123!"
        hashed = hash_password(plain)
        assert hashed != plain

    def test_verify_correct_password(self):
        plain = "SecurePass123!"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct_horse")
        assert verify_password("wrong_horse", hashed) is False

    def test_verify_invalid_hash_returns_false(self):
        # bcrypt raises ValueError on malformed hash — should return False
        assert verify_password("any_password", "not-a-valid-bcrypt-hash") is False


# ---------------------------------------------------------------------------
# content_schemas — get_schema_version
# ---------------------------------------------------------------------------

class TestGetSchemaVersion:
    def test_known_types_return_string(self):
        for ct in CONTENT_TYPE_SCHEMA_VERSIONS:
            v = get_schema_version(ct)
            assert isinstance(v, str)
            assert len(v) > 0

    def test_unknown_type_raises_key_error(self):
        with pytest.raises(KeyError, match="Unknown content type"):
            get_schema_version("nonexistent_type")


# ---------------------------------------------------------------------------
# DiagnosticItemPayload
# ---------------------------------------------------------------------------

class TestDiagnosticItemPayload:
    def _make_valid(self, **overrides):
        base = {
            "caps_ref": "4.MATH.1.1",
            "question": "What is 1/2 of 8?",
            "options": ["4", "2", "8", "16"],
            "correct_answer_index": 0,
            "explanation": "Half of 8 is 4 because 8 divided by 2 equals 4.",
            "bloom_level": "knowledge",
            "difficulty_band": "easy",
        }
        base.update(overrides)
        return base

    def test_valid_payload_accepted(self):
        data = self._make_valid()
        item = DiagnosticItemPayload.model_validate(data)
        assert item.caps_ref == "4.MATH.1.1"
        assert item.correct_answer_index == 0

    def test_missing_required_field_raises(self):
        from pydantic import ValidationError
        data = self._make_valid()
        del data["caps_ref"]
        with pytest.raises(ValidationError):
            DiagnosticItemPayload.model_validate(data)

    def test_correct_index_out_of_range_raises(self):
        from pydantic import ValidationError
        data = self._make_valid(correct_answer_index=10)
        with pytest.raises(ValidationError):
            DiagnosticItemPayload.model_validate(data)

    def test_duplicate_options_raises(self):
        from pydantic import ValidationError
        data = self._make_valid(options=["4", "4", "8", "16"])
        with pytest.raises(ValidationError):
            DiagnosticItemPayload.model_validate(data)
