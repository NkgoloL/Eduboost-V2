"""Educational Safety & Adverse Consequences Monitoring Service (LEV-WS11).

Detects leading indicators of educational harm: cognitive overload, hint exhaustion,
rapid guessing, and acute frustration. Enforces stop-work safeguards and cooldown
recommendations to protect learner emotional and cognitive well-being.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Sequence


class SafetySeverity(str, Enum):
    NOMINAL = "nominal"
    ELEVATED = "elevated"
    CRITICAL_STOP_WORK = "critical_stop_work"


@dataclass(frozen=True)
class LearnerSafetyStatus:
    learner_pseudonym: str
    severity: SafetySeverity
    frustration_index: float
    cognitive_overload_flag: bool
    hint_exhaustion_count: int
    rapid_guessing_count: int
    consecutive_struggles: int
    recommended_action: str
    evidence_type: str = "synthetic_fixture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "learner_pseudonym": self.learner_pseudonym,
            "severity": self.severity.value,
            "frustration_index": round(self.frustration_index, 4),
            "cognitive_overload_flag": self.cognitive_overload_flag,
            "hint_exhaustion_count": self.hint_exhaustion_count,
            "rapid_guessing_count": self.rapid_guessing_count,
            "consecutive_struggles": self.consecutive_struggles,
            "recommended_action": self.recommended_action,
            "evidence_type": self.evidence_type,
        }


def analyze_interaction_safety(
    learner_pseudonym: str,
    recent_events: Sequence[Dict[str, Any]],
    rapid_latency_threshold_ms: int = 1500,
    max_consecutive_struggles_before_halt: int = 3,
) -> LearnerSafetyStatus:
    """Analyze a temporal stream of interaction events for adverse pedagogical effects."""
    if not recent_events:
        return LearnerSafetyStatus(
            learner_pseudonym=learner_pseudonym,
            severity=SafetySeverity.NOMINAL,
            frustration_index=0.0,
            cognitive_overload_flag=False,
            hint_exhaustion_count=0,
            rapid_guessing_count=0,
            consecutive_struggles=0,
            recommended_action="Continue nominal adaptive practice.",
        )

    hint_exhaustions = 0
    rapid_guesses = 0
    consecutive_struggles = 0
    max_consecutive = 0

    for evt in recent_events:
        latency = evt.get("response_latency_ms")
        hints = evt.get("hint_count", 0)
        attempts = evt.get("attempt_count", 1)
        correct = evt.get("first_attempt_correct", True)

        is_rapid = latency is not None and latency < rapid_latency_threshold_ms
        is_hint_exhausted = hints >= 2
        is_struggle = (not correct) or attempts > 2 or is_hint_exhausted

        if is_rapid:
            rapid_guesses += 1
        if is_hint_exhausted:
            hint_exhaustions += 1

        if is_struggle:
            consecutive_struggles += 1
            if consecutive_struggles > max_consecutive:
                max_consecutive = consecutive_struggles
        else:
            consecutive_struggles = 0

    total_events = len(recent_events)
    # Frustration index bounded [0, 1]
    f_score = min(
        1.0,
        (0.3 * (rapid_guesses / max(1, total_events)))
        + (0.4 * (hint_exhaustions / max(1, total_events)))
        + (0.3 * min(1.0, max_consecutive / float(max_consecutive_struggles_before_halt))),
    )

    overload = (max_consecutive >= max_consecutive_struggles_before_halt) or (f_score >= 0.70)

    if max_consecutive >= max_consecutive_struggles_before_halt or f_score >= 0.75:
        severity = SafetySeverity.CRITICAL_STOP_WORK
        action = (
            "HALT active progression immediately. Trigger pedagogical cooldown break (15 min) "
            "and alert classroom teacher for human diagnostic check-in."
        )
    elif f_score >= 0.40 or hint_exhaustions >= 2:
        severity = SafetySeverity.ELEVATED
        action = "Provide step-by-step worked example and reduce item difficulty level by 1 step."
    else:
        severity = SafetySeverity.NOMINAL
        action = "Continue nominal adaptive practice."

    return LearnerSafetyStatus(
        learner_pseudonym=learner_pseudonym,
        severity=severity,
        frustration_index=f_score,
        cognitive_overload_flag=overload,
        hint_exhaustion_count=hint_exhaustions,
        rapid_guessing_count=rapid_guesses,
        consecutive_struggles=max_consecutive,
        recommended_action=action,
    )
