from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class SpacedReviewPlan:
    interval_days: int
    easiness_factor: float
    next_review_at: datetime


class SpacedRepetitionScheduler:
    """Small SM-2 variant for primary-school retrieval practice."""

    def update_schedule(self, *, correct: bool, interval_days: int = 0, easiness_factor: float = 2.5) -> SpacedReviewPlan:
        if not correct:
            interval = 1
            ef = max(1.3, easiness_factor - 0.2)
        elif interval_days <= 0:
            interval = 1
            ef = easiness_factor
        elif interval_days == 1:
            interval = 3
            ef = min(3.0, easiness_factor + 0.1)
        else:
            ef = min(3.0, easiness_factor + 0.1)
            interval = max(1, round(interval_days * ef))
        return SpacedReviewPlan(interval, round(ef, 2), datetime.now(timezone.utc) + timedelta(days=interval))
