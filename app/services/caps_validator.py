from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches


CAPS_SCOPE: dict[int, dict[str, tuple[str, ...]]] = {
    0: {
        "mathematics": ("counting", "patterns", "measurement", "shapes"),
        "english": ("phonics", "vocabulary", "listening", "storytelling"),
        "life skills": ("healthy habits", "creative arts", "movement", "community"),
    },
    1: {
        "mathematics": ("number sense", "addition", "measurement", "patterns"),
        "english": ("phonics", "reading", "sentence building", "oral language"),
        "life skills": ("personal wellbeing", "creative arts", "physical education", "environment"),
    },
    2: {
        "mathematics": ("addition", "subtraction", "place value", "measurement"),
        "english": ("reading comprehension", "spelling", "grammar", "writing"),
        "life skills": ("healthy habits", "citizenship", "creative arts", "movement"),
    },
    3: {
        "mathematics": ("fractions", "multiplication", "division", "data handling"),
        "english": ("reading comprehension", "creative writing", "grammar", "vocabulary"),
        "life skills": ("ubuntu", "safety", "relationships", "environment"),
        "natural sciences & technology": ("animals and plants", "materials", "energy", "earth"),
        "social sciences": ("maps", "history", "community", "government"),
    },
    4: {
        "mathematics": ("fractions", "decimals", "geometry", "problem solving"),
        "english": ("language structures", "comprehension", "creative writing", "oral presentation"),
        "natural sciences & technology": ("matter", "energy", "ecosystems", "planet earth"),
        "social sciences": ("history of sa", "map skills", "resources", "settlements"),
        "creative arts": ("music", "drama", "dance", "visual arts"),
    },
    5: {
        "mathematics": ("fractions", "percentages", "measurement", "data handling"),
        "english": ("novel study", "grammar", "transactional writing", "oral communication"),
        "natural sciences & technology": ("adaptations", "plants", "electrical circuits", "matter"),
        "social sciences": ("african history", "geography", "climate", "trade"),
        "economic & management sciences": ("needs and wants", "savings", "entrepreneurship", "resources"),
    },
    6: {
        "mathematics": ("ratios", "integers", "geometry", "algebra"),
        "english": ("language conventions", "creative writing", "poetry", "reading"),
        "natural sciences & technology": ("photosynthesis", "electricity", "weather", "forces"),
        "social sciences": ("democracy", "colonial history", "population", "natural resources"),
        "economic & management sciences": ("budgets", "markets", "entrepreneurship", "financial literacy"),
    },
    7: {
        "mathematics": ("algebra", "integers", "geometry", "probability"),
        "english": ("literature", "writing", "grammar", "oral communication"),
        "natural sciences & technology": ("ecosystems", "chemical change", "energy transfer", "solar system"),
        "social sciences": ("apartheid", "democracy", "population studies", "development issues"),
        "economic & management sciences": ("accounting basics", "budgets", "economic systems", "entrepreneurship"),
    },
}


def _normalise(value: str) -> str:
    return " ".join(value.lower().replace("&", "and").replace("/", " ").split())


@dataclass(slots=True)
class CAPSValidationResult:
    caps_aligned: bool
    canonical_subject: str
    canonical_topic: str | None
    reason: str


class CAPSAlignmentValidator:
    def validate(self, grade: int, subject: str, topic: str, content: str = "", term: int | None = None) -> CAPSValidationResult:
        canonical_subject = _normalise(subject)
        canonical_topic = _normalise(topic)
        allowed_topics = CAPS_SCOPE.get(grade, {}).get(canonical_subject, ())

        if not allowed_topics:
            return CAPSValidationResult(
                caps_aligned=False,
                canonical_subject=canonical_subject,
                canonical_topic=None,
                reason=f"No CAPS scope configured for grade {grade} {subject}",
            )

        for allowed in allowed_topics:
            if allowed in canonical_topic or canonical_topic in allowed:
                return CAPSValidationResult(
                    caps_aligned=True,
                    canonical_subject=canonical_subject,
                    canonical_topic=allowed,
                    reason="Requested topic is within CAPS scope",
                )

        content_blob = _normalise(content)
        if content_blob:
            for allowed in allowed_topics:
                if allowed in content_blob:
                    return CAPSValidationResult(
                        caps_aligned=True,
                        canonical_subject=canonical_subject,
                        canonical_topic=allowed,
                        reason="Generated content matched an allowed CAPS topic",
                    )

        suggestion = self.suggest_topic(grade, subject, topic)
        return CAPSValidationResult(
            caps_aligned=False,
            canonical_subject=canonical_subject,
            canonical_topic=suggestion,
            reason=f"Topic '{topic}' is outside CAPS scope for grade {grade} {subject}",
        )

    def suggest_topic(self, grade: int, subject: str, topic: str) -> str | None:
        canonical_subject = _normalise(subject)
        canonical_topic = _normalise(topic)
        allowed_topics = CAPS_SCOPE.get(grade, {}).get(canonical_subject, ())
        if not allowed_topics:
            return None
        matches = get_close_matches(canonical_topic, allowed_topics, n=1, cutoff=0.1)
        return matches[0] if matches else allowed_topics[0]

    def validate_generated_content(self, grade: int, subject: str, topic: str, content: str) -> CAPSValidationResult:
        request_validation = self.validate(grade, subject, topic)
        if not request_validation.caps_aligned:
            return request_validation

        canonical_topic = request_validation.canonical_topic or _normalise(topic)
        content_blob = _normalise(content)
        topic_tokens = [token for token in canonical_topic.split() if len(token) > 2]
        if any(token in content_blob for token in topic_tokens):
            return CAPSValidationResult(
                caps_aligned=True,
                canonical_subject=request_validation.canonical_subject,
                canonical_topic=canonical_topic,
                reason="Generated content reinforced the requested CAPS topic",
            )

        return CAPSValidationResult(
            caps_aligned=False,
            canonical_subject=request_validation.canonical_subject,
            canonical_topic=canonical_topic,
            reason=f"Generated content drifted away from CAPS topic '{canonical_topic}'",
        )
