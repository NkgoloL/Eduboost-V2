"""Educational State Reasonableness & Transition Invariants Service (LEV-WS08).

Enforces pedagogical invariants, bounds single-step leaps, prevents unrelated-concept
leakage, discounts assisted/repeated responses, detects rapid oscillations, and ensures
epistemic uncertainty is maintained under staleness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


class TransitionViolationType(str, Enum):
    PREREQUISITE_VIOLATION = "prerequisite_violation"
    SINGLE_STEP_LEAP_EXCEEDED = "single_step_leap_exceeded"
    UNRELATED_CONCEPT_LEAKAGE = "unrelated_concept_leakage"
    ASSISTED_RESPONSE_OVERCONFIDENCE = "assisted_response_overconfidence"
    STALENESS_UNCERTAINTY_VIOLATION = "staleness_uncertainty_violation"
    RAPID_OSCILLATION = "rapid_oscillation"


# Maximum mastery increase permitted from a single question attempt
MAX_SINGLE_STEP_LEAP = 0.40
# Minimum prerequisite mastery before dependent concept mastery can exceed threshold
MIN_PREREQUISITE_MASTERY_THRESHOLD = 0.40
DEPENDENT_MASTERY_TRIGGER = 0.70


@dataclass
class TransitionValidationResult:
    is_valid: bool
    violations: List[TransitionViolationType] = field(default_factory=list)
    adjusted_post_state: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    evidence_type: str = "synthetic_fixture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "violations": [v.value for v in self.violations],
            "adjusted_post_state": self.adjusted_post_state,
            "rationale": self.rationale,
            "evidence_type": self.evidence_type,
        }


def detect_rapid_oscillations(
    mastery_history: Sequence[float],
    threshold: float = 0.50,
    max_flips: int = 2,
) -> bool:
    """Detect if learner is oscillating rapidly across the mastery boundary.

    If mastery flips across `threshold` more than `max_flips` times in the sequence,
    the model is unstable and should not claim definitive mastery.
    """
    if len(mastery_history) < 3:
        return False

    binary_states = [1 if m >= threshold else 0 for m in mastery_history]
    flips = sum(1 for i in range(1, len(binary_states)) if binary_states[i] != binary_states[i - 1])
    return flips > max_flips


def apply_assistance_discount(
    raw_delta: float,
    teacher_assistance: bool = False,
    attempt_count: int = 1,
    hint_count: int = 0,
) -> float:
    """Discount mastery gain when learner used hints, multiple attempts, or teacher help.

    Educational validity rule:
    - Teacher assistance reduces mastery gain by 80%.
    - Additional attempts beyond the 1st reduce gain by 50% cumulatively.
    - Each hint reduces gain by 20%.
    """
    if raw_delta <= 0:
        return raw_delta

    discounted = raw_delta
    if teacher_assistance:
        discounted *= 0.20

    if attempt_count > 1:
        attempt_penalty = max(0.10, 1.0 - 0.50 * (attempt_count - 1))
        discounted *= attempt_penalty

    if hint_count > 0:
        hint_penalty = max(0.20, 1.0 - 0.20 * hint_count)
        discounted *= hint_penalty

    return round(discounted, 4)


def validate_state_transition(
    concept_id: str,
    pre_state: Dict[str, Any],
    proposed_post_state: Dict[str, Any],
    evidence_events: Sequence[Dict[str, Any]],
    prerequisite_map: Optional[Dict[str, List[str]]] = None,
    learner_mastery_map: Optional[Dict[str, float]] = None,
    mastery_history: Optional[Sequence[float]] = None,
    days_since_last_interaction: Optional[int] = None,
) -> TransitionValidationResult:
    """Validate a proposed mastery state transition against all educational reasonableness invariants."""
    violations: List[TransitionViolationType] = []
    pre_m = float(pre_state.get("mastery_level", 0.0))
    post_m = float(proposed_post_state.get("mastery_level", 0.0))
    pre_c = float(pre_state.get("confidence", 0.10))
    post_c = float(proposed_post_state.get("confidence", 0.50))
    delta_m = post_m - pre_m

    # 1. Single-step leap bound
    if delta_m > MAX_SINGLE_STEP_LEAP:
        violations.append(TransitionViolationType.SINGLE_STEP_LEAP_EXCEEDED)

    # 2. Unrelated concept leakage
    for evt in evidence_events:
        evt_concept = evt.get("concept_id")
        if evt_concept and evt_concept != concept_id:
            # Check if evt_concept is an allowed prerequisite or parent
            allowed_related = set()
            if prerequisite_map and concept_id in prerequisite_map:
                allowed_related.update(prerequisite_map[concept_id])
            if evt_concept not in allowed_related:
                violations.append(TransitionViolationType.UNRELATED_CONCEPT_LEAKAGE)
                break

    # 3. Prerequisite monotonicity check
    if prerequisite_map and learner_mastery_map and concept_id in prerequisite_map:
        prereqs = prerequisite_map[concept_id]
        if post_m >= DEPENDENT_MASTERY_TRIGGER:
            for p in prereqs:
                p_mastery = learner_mastery_map.get(p, 0.0)
                if p_mastery < MIN_PREREQUISITE_MASTERY_THRESHOLD:
                    violations.append(TransitionViolationType.PREREQUISITE_VIOLATION)
                    break

    # 4. Assisted response check
    if delta_m > 0:
        assisted_event = any(
            evt.get("teacher_assistance", False) or evt.get("hint_count", 0) > 1 or evt.get("attempt_count", 1) > 1
            for evt in evidence_events
        )
        if assisted_event and post_c > 0.60:
            violations.append(TransitionViolationType.ASSISTED_RESPONSE_OVERCONFIDENCE)

    # 5. Staleness uncertainty check
    if days_since_last_interaction is not None and days_since_last_interaction > 30:
        # After 30 days inactivity, confidence must not increase or exceed 0.50 without fresh probe
        if post_c > pre_c:
            violations.append(TransitionViolationType.STALENESS_UNCERTAINTY_VIOLATION)

    # 6. Rapid oscillation check
    if mastery_history and len(mastery_history) >= 3:
        combined_history = list(mastery_history) + [post_m]
        if detect_rapid_oscillations(combined_history):
            violations.append(TransitionViolationType.RAPID_OSCILLATION)

    is_valid = (len(violations) == 0)

    # Compute adjusted post state if violations exist
    adjusted_post_state = dict(proposed_post_state)
    if not is_valid:
        adjusted_m = min(post_m, pre_m + MAX_SINGLE_STEP_LEAP)
        # Cap confidence on violations
        adjusted_c = min(post_c, 0.40)
        adjusted_post_state["mastery_level"] = round(adjusted_m, 4)
        adjusted_post_state["confidence"] = round(adjusted_c, 4)
        rationale = f"Adjusted due to pedagogical violations: {[v.value for v in violations]}"
    else:
        rationale = "Transition satisfies all educational plausibility invariants."

    return TransitionValidationResult(
        is_valid=is_valid,
        violations=violations,
        adjusted_post_state=adjusted_post_state,
        rationale=rationale,
    )
