from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

PII_REPLACEMENTS = (
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[redacted-email]"),
    (re.compile(r"\b(?:\+27|0)[6-8][0-9][\s-]?[0-9]{3}[\s-]?[0-9]{4}\b"), "[redacted-phone]"),
    (re.compile(r"\b\d{13}\b"), "[redacted-id-number]"),
)

SA_CONTEXT_TERMS = (
    "south african", "south africa", "rands", "rand", "taxi", "spaza", "braai",
    "limpopo", "durban", "cape town", "johannesburg", "school", "community",
)


@dataclass(frozen=True, slots=True)
class ContentQualityScore:
    correctness: float
    caps_alignment: float
    clarity: float
    readability: float
    pedagogical_completeness: float
    inclusiveness: float
    safety: float

    @property
    def overall(self) -> float:
        return round(
            (
                self.correctness
                + self.caps_alignment
                + self.clarity
                + self.readability
                + self.pedagogical_completeness
                + self.inclusiveness
                + self.safety
            )
            / 7,
            3,
        )


def redact_pii_text(value: str) -> str:
    redacted = value
    for pattern, replacement in PII_REPLACEMENTS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def redact_pii(value: Any) -> Any:
    if isinstance(value, str):
        return redact_pii_text(value)
    if isinstance(value, list):
        return [redact_pii(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_pii(item) for item in value)
    if isinstance(value, dict):
        return {str(key): redact_pii(item) for key, item in value.items()}
    return value


def score_lesson_quality(*, content: str, caps_aligned: bool, answer_present: bool, has_worked_example: bool, has_practice: bool) -> ContentQualityScore:
    text = content.strip()
    word_count = len(text.split())
    clarity = 1.0 if 80 <= word_count <= 900 else 0.7 if word_count > 20 else 0.35
    readability = 1.0 if not re.search(r"\b[a-zA-Z]{18,}\b", text) else 0.75
    pedagogy = sum([has_worked_example, has_practice, answer_present]) / 3
    inclusiveness = 1.0 if any(term in text.lower() for term in SA_CONTEXT_TERMS) else 0.7
    safety = 0.0 if re.search(r"\b(explicit|gambling|hate|weapon|drug)\b", text, re.I) else 1.0
    return ContentQualityScore(
        correctness=1.0 if answer_present else 0.4,
        caps_alignment=1.0 if caps_aligned else 0.0,
        clarity=clarity,
        readability=readability,
        pedagogical_completeness=pedagogy,
        inclusiveness=inclusiveness,
        safety=safety,
    )
