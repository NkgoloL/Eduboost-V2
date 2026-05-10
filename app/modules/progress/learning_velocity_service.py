from __future__ import annotations

from datetime import datetime
from typing import Iterable


class LearningVelocityService:
    def compute_velocity(self, snapshots: Iterable[object]) -> float:
        ordered = sorted(snapshots, key=lambda s: getattr(s, "snapshot_at", getattr(s, "created_at", datetime.min)))
        if len(ordered) < 2:
            return 0.0
        first, last = ordered[0], ordered[-1]
        days = max(1.0, (getattr(last, "snapshot_at") - getattr(first, "snapshot_at")).total_seconds() / 86400)
        delta = float(getattr(last, "mastery_score")) - float(getattr(first, "mastery_score"))
        return round(delta / (days / 7.0), 4)

    def compute_risk_signal(self, mastery_score: float, days_since_last_activity: int, velocity: float) -> str:
        if mastery_score < 0.40 or days_since_last_activity > 30 or velocity < -0.05:
            return "urgent"
        if mastery_score < 0.60 or days_since_last_activity > 14 or velocity < 0:
            return "at_risk"
        return "on_track"

    def next_best_activities(self, mastery_rows: Iterable[object]) -> list[dict]:
        ranked = []
        for row in mastery_rows:
            score = float(getattr(row, "mastery_score", 0.0))
            caps_ref = getattr(row, "caps_ref", "")
            if score < 0.40:
                activity = "targeted_lesson"
                priority = 0
            elif score < 0.60:
                activity = "practice_drill"
                priority = 1
            elif score < 0.75:
                activity = "spaced_review"
                priority = 2
            else:
                activity = "extension_challenge"
                priority = 3
            ranked.append({"caps_ref": caps_ref, "activity": activity, "mastery_score": score, "priority": priority})
        return sorted(ranked, key=lambda r: (r["priority"], r["mastery_score"]))
