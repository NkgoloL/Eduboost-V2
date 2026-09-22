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


def test_validate_state_transition_prerequisite_violation():
    pre = {"mastery_level": 0.50, "confidence": 0.40}
    post = {"mastery_level": 0.80, "confidence": 0.55}  # Claiming mastery in multiplication
    events = [{"concept_id": "math.mult", "first_attempt_correct": True}]
    prereqs = {"math.mult": ["math.add"]}
    learner_masteries = {"math.add": 0.20}  # Addition is failing (0.20 < 0.40)
    res = validate_state_transition(
        "math.mult", pre, post, events,
        prerequisite_map=prereqs,
        learner_mastery_map=learner_masteries,
    )
    assert not res.is_valid
    assert TransitionViolationType.PREREQUISITE_VIOLATION in res.violations
