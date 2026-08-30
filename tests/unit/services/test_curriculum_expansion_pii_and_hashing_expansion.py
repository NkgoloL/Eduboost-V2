"""Comprehensive unit tests for Curriculum Expansion training data governance, hashing, and PII guardrails."""
from __future__ import annotations

import pytest

from app.services.curriculum_expansion import (
    record_sha256,
    dataset_sha256,
    forbidden_training_paths,
    obvious_pii_findings,
    validate_language_content,
    _normalised_json,
    ALLOWED_SOURCE_LICENSES,
    SAFE_STATUSES,
)


class TestCurriculumExpansionHashing:
    def test_normalised_json_deterministic(self):
        d1 = {"b": 2, "a": 1}
        d2 = {"a": 1, "b": 2}
        assert _normalised_json(d1) == _normalised_json(d2)
        assert _normalised_json(d1) == '{"a":1,"b":2}'

    def test_record_sha256_deterministic(self):
        r1 = {"title": "Lesson 1", "grade": 4}
        r2 = {"grade": 4, "title": "Lesson 1"}
        assert record_sha256(r1) == record_sha256(r2)

    def test_dataset_sha256_order_independent(self):
        h1 = "abc"
        h2 = "xyz"
        assert dataset_sha256([h1, h2]) == dataset_sha256([h2, h1])


class TestCurriculumExpansionGuardrails:
    def test_forbidden_training_paths(self):
        clean_payload = {"lesson_title": "Maths", "content": {"step": 1}}
        assert forbidden_training_paths(clean_payload) == []

        dirty_payload = {
            "lesson_title": "Maths",
            "metadata": {
                "learner_id": "12345",
                "nested": [{"email": "test@example.com"}],
            },
        }
        findings = forbidden_training_paths(dirty_payload)
        assert "$.metadata.learner_id" in findings
        assert "$.metadata.nested[0].email" in findings

    def test_obvious_pii_findings(self):
        clean_text = {"text": "Learn about fractions and decimals"}
        assert obvious_pii_findings(clean_text) == []

        dirty_email = {"text": "Contact user@example.com for support"}
        assert len(obvious_pii_findings(dirty_email)) > 0

    def test_validate_language_content(self):
        clean_en = {"text": "This is a clean English lesson"}
        assert validate_language_content(clean_en, "en") == []

        placeholder_en = {"text": "This is a TODO lesson with PLACEHOLDER text"}
        findings = validate_language_content(placeholder_en, "en")
        assert "placeholder_text" in findings

        invalid_lang = {"text": "Some text"}
        findings_lang = validate_language_content(invalid_lang, "unsupported_iso")
        assert "unsupported_language" in findings_lang

    def test_constants(self):
        assert "government_open" in ALLOWED_SOURCE_LICENSES
        assert "approved" in SAFE_STATUSES
