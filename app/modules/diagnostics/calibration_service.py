from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class CalibrationResult:
    item_id: str
    difficulty_b: float
    discrimination_a: float
    guessing_c: float
    review_required: bool
    response_count: int


class CalibrationService:
    """Lightweight item calibration from observed response data.

    This is intentionally conservative until the platform has enough live data:
    it updates difficulty from observed accuracy and flags unstable items for
    human review rather than overfitting sparse responses.
    """

    def calibrate_item(self, item: object, responses: list[object], *, min_responses: int = 100) -> CalibrationResult:
        response_count = len(responses)
        current_b = float(getattr(item, "difficulty_b", 0.0) or 0.0)
        current_a = float(getattr(item, "discrimination_a", 1.0) or 1.0)
        current_c = float(getattr(item, "guessing_c", 0.25) or 0.25)
        if response_count < min_responses:
            return CalibrationResult(str(getattr(item, "item_id", "")), current_b, current_a, current_c, False, response_count)
        accuracy = mean(1.0 if getattr(r, "is_correct", bool(r)) else 0.0 for r in responses)
        estimated_b = max(-3.0, min(3.0, (0.5 - accuracy) * 4.0))
        estimated_a = max(0.5, min(2.5, current_a + (0.5 - abs(accuracy - 0.5))))
        estimated_c = max(0.0, min(0.35, current_c))
        return CalibrationResult(str(getattr(item, "item_id", "")), round(estimated_b, 4), round(estimated_a, 4), round(estimated_c, 4), abs(estimated_b - current_b) > 0.5, response_count)
