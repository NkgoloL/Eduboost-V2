"""Comprehensive unit tests for curriculum expansion and training dataset governance."""
from __future__ import annotations

import pytest

from app.services.curriculum_expansion import (
    forbidden_training_paths,
    obvious_pii_findings,
    validate_language_content,
    record_sha256,
    dataset_sha256,
    ALLOWED_SOURCE_LICENSES,
    SAFE_STATUSES,
)


class TestCurriculumExpansionSafety:
    def test_forbidden_training_paths_detection(self):
        clean_dict = {"title": "Maths Grade 4", "content": {"text": "Numbers 1-100"}}
        assert forbidden_training_paths(clean_dict) == []

        dirty_dict = {
            "title": "Maths",
            "learner_id": "l-123",
            "metadata": {"user_id": "u-456", "email": "test@eduboost.co.za"},
        }
        findings = forbidden_training_paths(dirty_dict)
        assert len(findings) == 3
        assert "$.learner_id" in findings
        assert "$.metadata.user_id" in findings
        assert "$.metadata.email" in findings

    def test_obvious_pii_findings(self):
        clean = {"text": "Learn mathematics with numbers and equations."}
        assert obvious_pii_findings(clean) == []

        with_email = {"contact": "support@eduboost.co.za"}
        assert len(obvious_pii_findings(with_email)) >= 1

        with_phone = {"phone": "0821234567"}
        assert len(obvious_pii_findings(with_phone)) >= 1

        with_id = {"id_number": "8001015009087"}
        assert len(obvious_pii_findings(with_id)) >= 1

    def test_validate_language_content(self):
        clean_en = {"title": "Addition and Subtraction", "content": "Add 5 + 5 to make 10."}
        assert validate_language_content(clean_en, "en") == []

        with_placeholder = {"title": "TODO: Lesson Title", "content": "TBD"}
        issues = validate_language_content(with_placeholder, "en")
        assert "placeholder_text" in issues

        unsupported_lang = {"title": "Math", "content": "Content"}
        issues = validate_language_content(unsupported_lang, "fr")
        assert "unsupported_language" in issues

    def test_record_and_dataset_sha256(self):
        r1 = {"title": "Lesson 1", "grade": 4}
        r2 = {"title": "Lesson 2", "grade": 4}
        h1 = record_sha256(r1)
        h2 = record_sha256(r2)
        assert len(h1) == 64
        assert len(h2) == 64
        assert h1 != h2

        dh = dataset_sha256([h1, h2])
        assert len(dh) == 64

    def test_constants_definitions(self):
        assert "government_open" in ALLOWED_SOURCE_LICENSES
        assert "approved" in SAFE_STATUSES
