"""Comprehensive unit tests for CAPSAlignmentValidator and normalization functions."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.caps_validator import (
    _normalise,
    CAPSValidationResult,
    CAPSAlignmentValidator,
)


class TestCAPSValidator:
    def test_normalise_string_operations(self):
        assert _normalise("Mathematics & Statistics") == "mathematics and statistics"
        assert _normalise("Life_Sciences/Biology") == "life sciences biology"
        assert _normalise("   NATURAL   SCIENCES   ") == "natural sciences"

    def test_caps_validation_result_dataclass(self):
        res = CAPSValidationResult(
            caps_aligned=True,
            canonical_subject="mathematics",
            canonical_topic="Common Fractions",
            reason="Exact match",
            caps_reference="4.M.1.1",
            curriculum_version="2026.1",
            alignment_confidence=0.95,
        )
        assert res.caps_aligned is True
        assert res.canonical_subject == "mathematics"
        assert res.caps_reference == "4.M.1.1"

    def test_caps_alignment_validator_unknown_scope(self):
        mock_map = MagicMock()
        mock_map.find_topic.return_value = None
        mock_map.suggest_topic.return_value = None
        mock_map.version = "1.0"

        validator = CAPSAlignmentValidator(topic_map=mock_map)
        res = validator.validate(grade=12, subject="Quantum Physics", topic="Superposition")
        assert res.caps_aligned is False
        assert "No CAPS scope configured" in res.reason

    def test_caps_alignment_validator_suggested_outside_scope(self):
        mock_map = MagicMock()
        mock_map.find_topic.return_value = None
        mock_suggestion = MagicMock(topic="Algebra", subtopic="Equations", phase="Senior", term=1, prerequisites=[], assessment_standards=[], caps_reference="8.M.1")
        mock_map.suggest_topic.return_value = mock_suggestion
        mock_map.topics_for.return_value = []
        mock_map.version = "1.0"

        validator = CAPSAlignmentValidator(topic_map=mock_map)
        res = validator.validate(grade=8, subject="Mathematics", topic="Random Stuff", content="")
        assert res.caps_aligned is False
        assert "outside CAPS scope" in res.reason

    def test_caps_alignment_validator_validate_generated_content_reinforced(self):
        mock_map = MagicMock()
        matched_topic = MagicMock(topic="fractions", subtopic="addition", phase="Intermediate", term=2, prerequisites=[], assessment_standards=[], caps_reference="5.M.2")
        mock_map.find_topic.return_value = matched_topic
        mock_map.get.return_value = matched_topic
        mock_map.suggest_topic.return_value = matched_topic
        mock_map.version = "1.0"

        validator = CAPSAlignmentValidator(topic_map=mock_map)
        res = validator.validate_generated_content(
            grade=5,
            subject="Mathematics",
            topic="fractions",
            content="Today we learn fractions and practice addition of them",
        )
        assert res.caps_aligned is True
        assert res.alignment_confidence == 1.0
        assert "reinforced" in res.reason

    def test_caps_alignment_validator_alignment_confidence_with_content(self):
        mock_map = MagicMock()
        matched_topic = MagicMock(topic="fractions", subtopic="addition", phase="Intermediate", term=2, prerequisites=[], assessment_standards=[], caps_reference="5.M.2")
        mock_map.find_topic.return_value = matched_topic
        mock_map.version = "1.0"

        validator = CAPSAlignmentValidator(topic_map=mock_map)
        res = validator.validate(
            grade=5,
            subject="Mathematics",
            topic="fractions",
            content="We study fractions here",
        )
        assert res.caps_aligned is True
        assert res.alignment_confidence == 1.0

