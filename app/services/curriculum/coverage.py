from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any

from app.services.curriculum.caps_topic_map import CAPSTopicMap


@dataclass(frozen=True, slots=True)
class CurriculumGap:
    caps_reference: str
    grade: int
    subject: str
    topic: str
    missing_lessons: bool
    missing_diagnostics: bool
    missing_reviewed_content: bool


class CurriculumCoverageAnalyzer:
    def __init__(self, topic_map: CAPSTopicMap | None = None) -> None:
        self.topic_map = topic_map or CAPSTopicMap()

    def detect_gaps(self, *, lessons: Iterable[Mapping[str, Any]], diagnostic_items: Iterable[Mapping[str, Any]]) -> list[CurriculumGap]:
        lesson_refs = {row.get("caps_reference") for row in lessons if row.get("caps_reference")}
        reviewed_lesson_refs = {row.get("caps_reference") for row in lessons if row.get("caps_reference") and row.get("quality_reviewed")}
        item_refs = {row.get("caps_reference") for row in diagnostic_items if row.get("caps_reference")}
        gaps: list[CurriculumGap] = []
        for topic in self.topic_map.topics:
            missing_lessons = topic.reference not in lesson_refs
            missing_items = topic.reference not in item_refs
            missing_reviewed = topic.reference not in reviewed_lesson_refs
            if missing_lessons or missing_items or missing_reviewed:
                gaps.append(
                    CurriculumGap(
                        caps_reference=topic.reference,
                        grade=topic.grade,
                        subject=topic.subject,
                        topic=topic.topic,
                        missing_lessons=missing_lessons,
                        missing_diagnostics=missing_items,
                        missing_reviewed_content=missing_reviewed,
                    )
                )
        return gaps
