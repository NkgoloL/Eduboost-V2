from __future__ import annotations

from app.modules.progress.learning_velocity_service import LearningVelocityService
from app.modules.progress.mastery_model import MasteryLabel, compute_mastery_score, label_for_score, theta_to_mastery


def test_mastery_weighting_and_labels():
    low = compute_mastery_score(theta=-2.0, se=1.2, practice_accuracy=0.2, recency_days=30, consistency_ratio=0.2)
    high = compute_mastery_score(theta=2.0, se=0.2, practice_accuracy=0.95, recency_days=0, consistency_ratio=0.9)
    assert 0 <= low < high <= 1
    assert label_for_score(0.35) == MasteryLabel.NEEDS_PRACTICE
    assert label_for_score(0.95) == MasteryLabel.MASTERED
    assert theta_to_mastery(0) == 0.5


def test_next_best_activity_ordering():
    class Row:
        def __init__(self, caps_ref, score):
            self.caps_ref = caps_ref
            self.mastery_score = score
    activities = LearningVelocityService().next_best_activities([Row("4.M.1.1", 0.3), Row("4.M.1.2", 0.8)])
    assert activities[0]["activity"] == "targeted_lesson"
