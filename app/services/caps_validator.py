from __future__ import annotations

from dataclasses import dataclass

from app.services.curriculum.caps_topic_map import CAPSTopic, CAPSTopicMap


def _normalise(value: str) -> str:
    return " ".join(value.lower().replace("&", "and").replace("/", " ").replace("_", " ").split())


@dataclass(slots=True)
class CAPSValidationResult:
    caps_aligned: bool
    canonical_subject: str
    canonical_topic: str | None
    reason: str
    caps_reference: str | None = None
    curriculum_version: str | None = None
    alignment_confidence: float = 0.0
    phase: str | None = None
    term: int | None = None
    subtopic: str | None = None
    prerequisites: tuple[str, ...] = ()
    assessment_standards: tuple[str, ...] = ()


class CAPSAlignmentValidator:
    def __init__(self, topic_map: CAPSTopicMap | None = None) -> None:
        self.topic_map = topic_map or CAPSTopicMap()

    def validate(self, grade: int, subject: str, topic: str, content: str = "", term: int | None = None) -> CAPSValidationResult:
        canonical_subject = _normalise(subject)
        matched = self.topic_map.find_topic(grade, canonical_subject, topic)
        if matched is not None and (term is None or matched.term == term):
            confidence = self._alignment_confidence(matched, topic_text=topic, content=content)
            return self._result(True, canonical_subject, matched, "Requested topic is within the canonical CAPS topic map", confidence)

        if content:
            for candidate in self.topic_map.topics_for(grade, canonical_subject):
                if self._topic_mentioned(candidate, content):
                    return self._result(True, canonical_subject, candidate, "Generated content referenced a valid CAPS topic", 0.75)

        suggestion = self.topic_map.suggest_topic(grade, subject, topic)
        if suggestion is None:
            return CAPSValidationResult(
                caps_aligned=False,
                canonical_subject=canonical_subject,
                canonical_topic=None,
                reason=f"No CAPS scope configured for grade {grade} {subject}",
                curriculum_version=self.topic_map.version,
            )
        return self._result(False, canonical_subject, suggestion, f"Topic '{topic}' is outside CAPS scope for grade {grade} {subject}", 0.0)

    def suggest_topic(self, grade: int, subject: str, topic: str) -> str | None:
        suggested = self.topic_map.suggest_topic(grade, subject, topic)
        return suggested.topic if suggested else None

    def validate_generated_content(self, grade: int, subject: str, topic: str, content: str) -> CAPSValidationResult:
        request_validation = self.validate(grade, subject, topic)
        if not request_validation.caps_aligned:
            return request_validation
        matched = self.topic_map.get(request_validation.caps_reference or "") or self.topic_map.find_topic(grade, subject, topic)
        if matched and self._topic_mentioned(matched, content):
            return self._result(True, request_validation.canonical_subject, matched, "Generated content reinforced the requested CAPS topic", 1.0)
        return CAPSValidationResult(
            caps_aligned=False,
            canonical_subject=request_validation.canonical_subject,
            canonical_topic=request_validation.canonical_topic,
            reason=f"Generated content drifted away from CAPS topic '{request_validation.canonical_topic}'",
            caps_reference=request_validation.caps_reference,
            curriculum_version=self.topic_map.version,
            alignment_confidence=0.0,
            phase=request_validation.phase,
            term=request_validation.term,
            subtopic=request_validation.subtopic,
            prerequisites=request_validation.prerequisites,
            assessment_standards=request_validation.assessment_standards,
        )

    def validate_caps_reference(self, reference: str) -> CAPSValidationResult:
        matched = self.topic_map.get(reference)
        if matched is None:
            return CAPSValidationResult(False, "", None, "Unknown CAPS reference", reference, self.topic_map.version, 0.0)
        return self._result(True, matched.subject, matched, "CAPS reference exists in canonical map", 1.0)

    def coverage_summary(self) -> dict[str, object]:
        return self.topic_map.coverage_summary()

    def _alignment_confidence(self, topic: CAPSTopic, *, content: str, topic_text: str) -> float:
        score = 0.85 if _normalise(topic_text) == topic.topic else 0.7
        if content and self._topic_mentioned(topic, content):
            score = min(1.0, score + 0.15)
        return score

    def _topic_mentioned(self, topic: CAPSTopic, content: str) -> bool:
        blob = _normalise(content)
        topic_tokens = [token for token in topic.topic.split() if len(token) > 2]
        subtopic_tokens = [token for token in topic.subtopic.split() if len(token) > 2]
        return any(token in blob for token in topic_tokens + subtopic_tokens)

    def _result(self, aligned: bool, subject: str, topic: CAPSTopic, reason: str, confidence: float) -> CAPSValidationResult:
        return CAPSValidationResult(
            caps_aligned=aligned,
            canonical_subject=subject,
            canonical_topic=topic.topic,
            reason=reason,
            caps_reference=topic.reference,
            curriculum_version=self.topic_map.version,
            alignment_confidence=confidence,
            phase=topic.phase,
            term=topic.term,
            subtopic=topic.subtopic,
            prerequisites=topic.prerequisites,
            assessment_standards=topic.assessment_standards,
        )


CAPS_SCOPE: dict[int, dict[str, tuple[str, ...]]] = {}
for _topic in CAPSTopicMap().topics:
    CAPS_SCOPE.setdefault(_topic.grade, {}).setdefault(_topic.subject, tuple())
    CAPS_SCOPE[_topic.grade][_topic.subject] = tuple(sorted(set(CAPS_SCOPE[_topic.grade][_topic.subject] + (_topic.topic,))))
