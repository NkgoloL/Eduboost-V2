from __future__ import annotations

from dataclasses import dataclass, field
from difflib import get_close_matches
from typing import Iterable

CURRICULUM_MAP_VERSION = "caps-mvp-2026.05"


def _normalise(value: str) -> str:
    return " ".join(value.lower().replace("&", "and").replace("/", " ").replace("_", " ").split())


@dataclass(frozen=True, slots=True)
class CAPSTopic:
    phase: str
    grade: int
    subject: str
    term: int
    topic: str
    subtopic: str
    prerequisites: tuple[str, ...] = field(default_factory=tuple)
    assessment_standards: tuple[str, ...] = field(default_factory=tuple)

    @property
    def reference(self) -> str:
        return (
            f"CAPS:{CURRICULUM_MAP_VERSION}:G{self.grade}:"
            f"{_slug(self.subject)}:T{self.term}:{_slug(self.topic)}:{_slug(self.subtopic)}"
        )


def _slug(value: str) -> str:
    return _normalise(value).replace(" ", "-")


_CAPS_TOPICS: tuple[CAPSTopic, ...] = (
    CAPSTopic("foundation", 0, "mathematics", 1, "counting", "numbers 1 to 10", (), ("Counts objects reliably",)),
    CAPSTopic("foundation", 0, "mathematics", 2, "patterns", "copy and extend patterns", ("counting"), ("Extends simple repeated patterns",)),
    CAPSTopic("foundation", 1, "mathematics", 1, "number sense", "counting and comparing", ("counting"), ("Compares small whole numbers",)),
    CAPSTopic("foundation", 2, "mathematics", 2, "place value", "tens and units", ("number sense",), ("Uses tens and units to represent numbers",)),
    CAPSTopic("foundation", 3, "mathematics", 2, "fractions", "halves quarters thirds", ("division",), ("Identifies and compares common fractions",)),
    CAPSTopic("intermediate", 4, "mathematics", 1, "fractions", "equivalent fractions", ("division",), ("Recognises and explains equivalent fractions",)),
    CAPSTopic("intermediate", 4, "mathematics", 2, "decimals", "tenths and hundredths", ("fractions",), ("Links decimal notation to fractions",)),
    CAPSTopic("intermediate", 4, "mathematics", 3, "geometry", "2d shapes", (), ("Names and classifies two-dimensional shapes",)),
    CAPSTopic("intermediate", 4, "mathematics", 4, "problem solving", "multi-step word problems", ("multiplication", "division"), ("Solves contextual word problems",)),
    CAPSTopic("intermediate", 5, "mathematics", 1, "fractions", "compare and order fractions", ("equivalent fractions",), ("Orders fractions using equivalent forms",)),
    CAPSTopic("intermediate", 5, "mathematics", 2, "percentages", "percent as part of 100", ("fractions",), ("Represents percentages as fractions and decimals",)),
    CAPSTopic("intermediate", 6, "mathematics", 1, "ratios", "ratio language", ("fractions",), ("Uses ratio notation and language",)),
    CAPSTopic("senior", 7, "mathematics", 1, "algebra", "expressions", ("number sentences",), ("Writes and simplifies algebraic expressions",)),
    CAPSTopic("senior", 7, "mathematics", 2, "integers", "operations with integers", ("whole number operations",), ("Calculates with positive and negative integers",)),
    CAPSTopic("intermediate", 4, "english", 1, "comprehension", "main idea", ("reading"), ("Identifies main ideas and supporting detail",)),
    CAPSTopic("intermediate", 5, "english", 2, "grammar", "parts of speech", ("sentence building",), ("Uses nouns, verbs, adjectives and adverbs correctly",)),
    CAPSTopic("intermediate", 6, "natural sciences and technology", 1, "photosynthesis", "plants make food", ("plants",), ("Explains the basic process of photosynthesis",)),
    CAPSTopic("intermediate", 4, "social sciences", 2, "map skills", "symbols and keys", (), ("Uses symbols and keys on maps",)),
)


class CAPSTopicMap:
    def __init__(self, topics: Iterable[CAPSTopic] = _CAPS_TOPICS, version: str = CURRICULUM_MAP_VERSION) -> None:
        self.version = version
        self._topics = tuple(topics)
        self._by_reference = {topic.reference: topic for topic in self._topics}

    @property
    def topics(self) -> tuple[CAPSTopic, ...]:
        return self._topics

    def subjects_for_grade(self, grade: int) -> tuple[str, ...]:
        return tuple(sorted({topic.subject for topic in self._topics if topic.grade == grade}))

    def topics_for(self, grade: int, subject: str) -> tuple[CAPSTopic, ...]:
        canonical_subject = _normalise(subject)
        return tuple(topic for topic in self._topics if topic.grade == grade and topic.subject == canonical_subject)

    def find_topic(self, grade: int, subject: str, topic: str, subtopic: str | None = None) -> CAPSTopic | None:
        canonical_topic = _normalise(topic)
        canonical_subtopic = _normalise(subtopic or "")
        candidates = self.topics_for(grade, subject)
        for candidate in candidates:
            if candidate.topic == canonical_topic and (not canonical_subtopic or candidate.subtopic == canonical_subtopic):
                return candidate
            if candidate.topic in canonical_topic or canonical_topic in candidate.topic:
                return candidate
            if canonical_subtopic and (candidate.subtopic in canonical_subtopic or canonical_subtopic in candidate.subtopic):
                return candidate
        return None

    def get(self, reference: str) -> CAPSTopic | None:
        return self._by_reference.get(reference)

    def suggest_topic(self, grade: int, subject: str, requested_topic: str) -> CAPSTopic | None:
        candidates = self.topics_for(grade, subject)
        if not candidates:
            return None
        topic_lookup = {candidate.topic: candidate for candidate in candidates}
        matches = get_close_matches(_normalise(requested_topic), list(topic_lookup), n=1, cutoff=0.1)
        return topic_lookup[matches[0]] if matches else candidates[0]

    def coverage_summary(self) -> dict[str, object]:
        by_grade: dict[int, dict[str, int]] = {}
        for topic in self._topics:
            by_grade.setdefault(topic.grade, {}).setdefault(topic.subject, 0)
            by_grade[topic.grade][topic.subject] += 1
        return {"version": self.version, "topic_count": len(self._topics), "grades": by_grade}
