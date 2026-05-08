from __future__ import annotations

from app.services.caps_validator import CAPSAlignmentValidator
from app.services.curriculum.caps_topic_map import CAPSTopicMap


def test_caps_topic_map_exposes_canonical_reference() -> None:
    topic_map = CAPSTopicMap()
    topic = topic_map.find_topic(4, "Mathematics", "Fractions")
    assert topic is not None
    assert topic.reference.startswith("CAPS:cards") is False
    assert topic.reference.startswith("CAPS:")
    assert topic.phase == "intermediate"
    assert topic.assessment_standards


def test_caps_validator_returns_reference_and_confidence() -> None:
    result = CAPSAlignmentValidator().validate(4, "Mathematics", "Fractions", "Equivalent fractions use equal parts.")
    assert result.caps_aligned is True
    assert result.caps_reference is not None
    assert result.alignment_confidence > 0
    assert result.curriculum_version == "caps-mvp-2026.05"


def test_caps_reference_validator_rejects_unknown_reference() -> None:
    result = CAPSAlignmentValidator().validate_caps_reference("CAPS:unknown")
    assert result.caps_aligned is False
