from __future__ import annotations

from app.services.curriculum.coverage import CurriculumCoverageAnalyzer
from app.services.curriculum.caps_topic_map import CAPSTopicMap


def test_curriculum_coverage_detects_missing_lesson_and_item_refs() -> None:
    topic = CAPSTopicMap().find_topic(4, "mathematics", "fractions")
    assert topic is not None
    gaps = CurriculumCoverageAnalyzer().detect_gaps(
        lessons=[{"caps_reference": topic.reference, "quality_reviewed": True}],
        diagnostic_items=[],
    )
    assert any(gap.caps_reference == topic.reference and gap.missing_diagnostics for gap in gaps)
