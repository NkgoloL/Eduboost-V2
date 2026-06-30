"""Production-readiness contracts for diagnostics, assessment, item bank, and mastery.

This module is intentionally dependency-light.  It captures deterministic,
repository-verifiable behaviour for the production-readiness backlog while the
runtime services continue to own database/session orchestration.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence


class ItemReviewStatus(str, Enum):
    """Canonical diagnostic item review workflow states."""

    DRAFT = "draft"
    AI_GENERATED = "AI-generated"
    HUMAN_REVIEWED = "human-reviewed"
    APPROVED = "approved"
    RETIRED = "retired"


class BiasDimension(str, Enum):
    """Human-review dimensions for diagnostic item bias checks."""

    LANGUAGE = "language"
    REGION = "region"
    SOCIOECONOMIC_CONTEXT = "socioeconomic_context"


@dataclass(frozen=True)
class DiagnosticItemSpec:
    """Repository-side canonical diagnostic item schema.

    Required fields map directly to production-readiness item-bank requirements:
    item ID, subject, grade, topic, skill, difficulty, discrimination, correct
    answer, distractors, explanation, CAPS reference, review status, and
    misconception tags.
    """

    item_id: str
    subject: str
    grade: int
    topic: str
    skill: str
    difficulty: float
    discrimination: float
    correct_answer: str
    distractors: tuple[str, ...]
    explanation: str
    caps_reference: str
    review_status: ItemReviewStatus = ItemReviewStatus.DRAFT
    misconception_tags: tuple[str, ...] = field(default_factory=tuple)
    language: str = "en"
    region: str = "ZA"
    exposure_count: int = 0
    max_exposure: int = 50


def validate_diagnostic_item_schema(item: DiagnosticItemSpec) -> list[str]:
    """Return validation failures for a diagnostic item specification."""

    failures: list[str] = []
    required_text = {
        "item_id": item.item_id,
        "subject": item.subject,
        "topic": item.topic,
        "skill": item.skill,
        "correct_answer": item.correct_answer,
        "explanation": item.explanation,
        "caps_reference": item.caps_reference,
    }
    for field_name, value in required_text.items():
        if not str(value).strip():
            failures.append(f"{field_name} is required")
    if not (0 <= item.grade <= 12):
        failures.append("grade must be between 0 and 12")
    if not (-4.0 <= item.difficulty <= 4.0):
        failures.append("difficulty must be in [-4.0, 4.0]")
    if not (0.1 <= item.discrimination <= 4.0):
        failures.append("discrimination must be in [0.1, 4.0]")
    if len(item.distractors) < 1:
        failures.append("at least one distractor is required")
    if item.correct_answer in item.distractors:
        failures.append("correct answer must not appear as a distractor")
    if item.max_exposure < 1:
        failures.append("max_exposure must be positive")
    if item.exposure_count < 0:
        failures.append("exposure_count must be non-negative")
    return failures


def irt_probability(theta: float, difficulty: float, discrimination: float) -> float:
    """Compute overflow-safe two-parameter IRT probability."""

    theta = max(-5.0, min(5.0, theta))
    difficulty = max(-4.0, min(4.0, difficulty))
    discrimination = max(0.1, min(4.0, discrimination))
    exponent = -discrimination * (theta - difficulty)
    exponent = max(-35.0, min(35.0, exponent))
    return 1.0 / (1.0 + math.exp(exponent))


def fisher_information(theta: float, item: DiagnosticItemSpec) -> float:
    """Compute Fisher information for item selection."""

    probability = irt_probability(theta, item.difficulty, item.discrimination)
    return item.discrimination**2 * probability * (1.0 - probability)


def select_item_by_fisher_information(
    theta: float,
    items: Sequence[DiagnosticItemSpec],
    *,
    used_item_ids: Iterable[str] = (),
) -> DiagnosticItemSpec | None:
    """Select the highest-information eligible item not already used."""

    used = set(used_item_ids)
    candidates = [
        item
        for item in items
        if item.item_id not in used
        and item.review_status == ItemReviewStatus.APPROVED
        and item.exposure_count < item.max_exposure
        and not validate_diagnostic_item_schema(item)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: fisher_information(theta, item))


def grade_equivalent_from_theta(theta: float, learner_grade: int) -> float:
    """Map theta onto a conservative grade-equivalent signal.

    The mapping is deliberately bounded so diagnostic evidence does not overstate
    learner placement from a small item sample.
    """

    theta = max(-4.0, min(4.0, theta))
    bounded_delta = max(-1.5, min(1.5, theta * 0.375))
    return round(max(0.0, learner_grade + bounded_delta), 2)


def identify_gap_topics(responses: Sequence[Mapping[str, object]]) -> list[str]:
    """Identify ranked gap topics from incorrect diagnostic responses."""

    counts: dict[str, int] = {}
    for response in responses:
        if bool(response.get("correct")):
            continue
        topic = str(response.get("topic", "")).strip()
        if topic:
            counts[topic] = counts.get(topic, 0) + 1
    return [topic for topic, _count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def can_transition_review_status(current: ItemReviewStatus, target: ItemReviewStatus) -> bool:
    """Validate the item review workflow: draft -> AI-generated -> human-reviewed -> approved -> retired."""

    allowed = {
        ItemReviewStatus.DRAFT: {ItemReviewStatus.AI_GENERATED, ItemReviewStatus.HUMAN_REVIEWED},
        ItemReviewStatus.AI_GENERATED: {ItemReviewStatus.HUMAN_REVIEWED, ItemReviewStatus.RETIRED},
        ItemReviewStatus.HUMAN_REVIEWED: {ItemReviewStatus.APPROVED, ItemReviewStatus.RETIRED},
        ItemReviewStatus.APPROVED: {ItemReviewStatus.RETIRED},
        ItemReviewStatus.RETIRED: set(),
    }
    return target in allowed[current]


def audit_minimum_viable_item_bank(
    items: Sequence[DiagnosticItemSpec],
    *,
    launch_grades: Iterable[int],
    launch_subjects: Iterable[str],
    min_items_per_grade_subject: int = 1,
) -> list[str]:
    """Check launch grade/subject item coverage for the minimum viable bank."""

    failures: list[str] = []
    approved_items = [item for item in items if item.review_status == ItemReviewStatus.APPROVED]
    for grade in launch_grades:
        for subject in launch_subjects:
            count = sum(1 for item in approved_items if item.grade == grade and item.subject == subject)
            if count < min_items_per_grade_subject:
                failures.append(
                    f"grade {grade} subject {subject} has {count} approved item(s); "
                    f"requires {min_items_per_grade_subject}"
                )
    return failures


def required_bias_review_dimensions() -> tuple[BiasDimension, ...]:
    """Return mandatory human-review dimensions for bias and fairness."""

    return (
        BiasDimension.LANGUAGE,
        BiasDimension.REGION,
        BiasDimension.SOCIOECONOMIC_CONTEXT,
    )


def remediation_tags_from_misconceptions(item: DiagnosticItemSpec) -> tuple[str, ...]:
    """Return remediation routing tags derived from misconception metadata."""

    return tuple(sorted({tag.strip().lower() for tag in item.misconception_tags if tag.strip()}))
