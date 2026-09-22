import pytest

from app.services.educational_validation.state_reasonableness import (
    TransitionViolationType,
    apply_assistance_discount,
    detect_rapid_oscillations,
    validate_state_transition,
)


def test_detect_rapid_oscillations():
    stable_history = [0.2, 0.3, 0.4, 0.6, 0.7]
    assert not detect_rapid_oscillations(stable_history)

    oscillating_history = [0.2, 0.8, 0.3, 0.9, 0.2]
    assert detect_rapid_oscillations(oscillating_history)


def test_apply_assistance_discount():
    raw_delta = 0.20
    # No assistance
    clean_delta = apply_assistance_discount(raw_delta, teacher_assistance=False, attempt_count=1, hint_count=0)
    assert clean_delta == 0.20

    # With teacher assistance
    assisted_delta = apply_assistance_discount(raw_delta, teacher_assistance=True, attempt_count=1, hint_count=0)
    assert assisted_delta < 0.10

    # With multiple hints
    hinted_delta = apply_assistance_discount(raw_delta, teacher_assistance=False, attempt_count=1, hint_count=3)
    assert hinted_delta < clean_delta


def test_validate_state_transition_valid():
    pre = {"mastery_level": 0.30, "confidence": 0.20}
    post = {"mastery_level": 0.55, "confidence": 0.50}
    events = [{"concept_id": "math.add", "first_attempt_correct": True, "teacher_assistance": False}]
    res = validate_state_transition("math.add", pre, post, events)
    assert res.is_valid
    assert len(res.violations) == 0


def test_validate_state_transition_leap_exceeded():
    pre = {"mastery_level": 0.10, "confidence": 0.20}
    post = {"mastery_level": 0.90, "confidence": 0.50}  # Jump of 0.80 > 0.40
    events = [{"concept_id": "math.add", "first_attempt_correct": True}]
    res = validate_state_transition("math.add", pre, post, events)
    assert not res.is_valid
    assert TransitionViolationType.SINGLE_STEP_LEAP_EXCEEDED in res.violations


def test_validate_state_transition_unrelated_concept_leakage():
    pre = {"mastery_level": 0.30, "confidence": 0.20}
    post = {"mastery_level": 0.50, "confidence": 0.50}
    # Event is for science.matter, but transition is for math.add!
    events = [{"concept_id": "science.matter", "first_attempt_correct": True}]
    res = validate_state_transition("math.add", pre, post, events)
    assert not res.is_valid
    assert TransitionViolationType.UNRELATED_CONCEPT_LEAKAGE in res.violations


def test_detect_rapid_oscillations_short_history():
    assert not detect_rapid_oscillations([])
    assert not detect_rapid_oscillations([0.5, 0.6])


def test_apply_assistance_discount_edge_cases():
    # Negative delta
    assert apply_assistance_discount(-0.1) == -0.1
    # Multiple attempts and hints combined
    disc = apply_assistance_discount(0.40, attempt_count=3, hint_count=2)
    assert disc < 0.20


def test_validate_state_transition_staleness_violation():
    pre = {"mastery_level": 0.50, "confidence": 0.30}
    post = {"mastery_level": 0.55, "confidence": 0.50}  # Inactive for 40 days, confidence increased
    events = [{"concept_id": "math.add", "first_attempt_correct": True}]
    res = validate_state_transition("math.add", pre, post, events, days_since_last_interaction=40)
    assert not res.is_valid
    assert TransitionViolationType.STALENESS_UNCERTAINTY_VIOLATION in res.violations
    d = res.to_dict()
    assert d["is_valid"] is False
    assert "staleness_uncertainty_violation" in d["violations"]


def test_validate_state_transition_assisted_overconfidence():
    pre = {"mastery_level": 0.30, "confidence": 0.20}
    post = {"mastery_level": 0.50, "confidence": 0.70}  # Confidence 0.70 with teacher assistance
    events = [{"concept_id": "math.add", "teacher_assistance": True}]
    res = validate_state_transition("math.add", pre, post, events)
    assert not res.is_valid
    assert TransitionViolationType.ASSISTED_RESPONSE_OVERCONFIDENCE in res.violations


def test_validate_state_transition_oscillation_detected():
    pre = {"mastery_level": 0.60, "confidence": 0.40}
    post = {"mastery_level": 0.30, "confidence": 0.40}
    events = [{"concept_id": "math.add", "first_attempt_correct": False}]
    history = [0.2, 0.8, 0.2, 0.8]
    res = validate_state_transition("math.add", pre, post, events, mastery_history=history)
    assert not res.is_valid
    assert TransitionViolationType.RAPID_OSCILLATION in res.violations


def test_validate_state_transition_allowed_prerequisite_not_leakage():
    pre = {"mastery_level": 0.50, "confidence": 0.40}
    post = {"mastery_level": 0.60, "confidence": 0.45}
    # Event is for math.add, which is an allowed prerequisite for math.mult
    events = [{"concept_id": "math.add", "first_attempt_correct": True}]
    prereqs = {"math.mult": ["math.add"]}
    res = validate_state_transition("math.mult", pre, post, events, prerequisite_map=prereqs)
    assert res.is_valid
    assert TransitionViolationType.UNRELATED_CONCEPT_LEAKAGE not in res.violations


def test_validate_state_transition_prerequisite_violation():
    pre = {"mastery_level": 0.50, "confidence": 0.40}
    post = {"mastery_level": 0.75, "confidence": 0.50}  # post_m >= 0.70
    events = [{"concept_id": "math.mult", "first_attempt_correct": True}]
    prereqs = {"math.mult": ["math.add"]}
    mastery_map = {"math.add": 0.20}  # Prerequisite mastery < 0.40
    res = validate_state_transition(
        "math.mult", pre, post, events, prerequisite_map=prereqs, learner_mastery_map=mastery_map
    )
    assert not res.is_valid
    assert TransitionViolationType.PREREQUISITE_VIOLATION in res.violations
