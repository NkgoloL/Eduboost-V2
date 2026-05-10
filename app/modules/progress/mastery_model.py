from __future__ import annotations

import math
from enum import Enum


class MasteryLabel(str, Enum):
    NEEDS_PRACTICE = "needs_practice"
    DEVELOPING = "developing"
    ON_TRACK = "on_track"
    PROFICIENT = "proficient"
    MASTERED = "mastered"


def theta_to_mastery(theta: float) -> float:
    return max(0.0, min(1.0, 0.5 * (1.0 + math.erf(theta / math.sqrt(2.0)))))


def label_for_score(score: float) -> MasteryLabel:
    if score < 0.40:
        return MasteryLabel.NEEDS_PRACTICE
    if score < 0.60:
        return MasteryLabel.DEVELOPING
    if score < 0.75:
        return MasteryLabel.ON_TRACK
    if score < 0.90:
        return MasteryLabel.PROFICIENT
    return MasteryLabel.MASTERED


def compute_mastery_score(
    theta: float,
    se: float,
    practice_accuracy: float | None = None,
    recency_days: float = 0.0,
    consistency_ratio: float | None = None,
) -> float:
    mastery_theta = theta_to_mastery(theta) * max(0.0, min(1.0, 1.0 - (se / 2.0)))
    practice = 0.5 if practice_accuracy is None else max(0.0, min(1.0, practice_accuracy))
    recency = math.exp(-0.05 * max(0.0, recency_days))
    consistency = 0.5 if consistency_ratio is None else max(0.0, min(1.0, consistency_ratio))
    confidence = max(0.0, min(1.0, 1.0 - (se / 2.0)))
    score = (0.40 * mastery_theta) + (0.25 * practice) + (0.15 * recency) + (0.10 * consistency) + (0.10 * confidence)
    return round(max(0.0, min(1.0, score)), 4)
