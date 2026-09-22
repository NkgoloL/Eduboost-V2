import pytest

from app.domain.educational_validation_schemas import MAX_CONFIDENCE_THRESHOLD
from app.services.educational_validation.use_authorization import (
    enforce_confidence_bound,
    evaluate_use_authorization,
)


def test_enforce_confidence_bound():
    assert enforce_confidence_bound(0.45) == 0.45
    assert enforce_confidence_bound(0.60) == 0.60
    assert enforce_confidence_bound(0.95) == MAX_CONFIDENCE_THRESHOLD
    assert enforce_confidence_bound(-0.1) == 0.0


def test_evaluate_use_authorization_formative_permitted():
    decision = evaluate_use_authorization(
        decision_scope="formative_hinting",
        requested_confidence=0.85,
        content_grade=4,
    )
    assert decision.is_authorized
    assert decision.status == "authorised"
    assert decision.effective_confidence == MAX_CONFIDENCE_THRESHOLD


def test_evaluate_use_authorization_high_stakes_prohibited():
    decision = evaluate_use_authorization(
        decision_scope="formal_grading",
        requested_confidence=0.50,
        content_grade=4,
    )
    assert not decision.is_authorized
    assert decision.status == "unsupported"
    assert "prohibited" in decision.reason


def test_evaluate_use_authorization_grade_progression_prohibited():
    decision = evaluate_use_authorization(
        decision_scope="grade_progression",
        requested_confidence=0.55,
        content_grade=5,
    )
    assert not decision.is_authorized
    assert decision.status == "unsupported"


def test_evaluate_use_authorization_invalid_grade():
    decision = evaluate_use_authorization(
        decision_scope="low_stakes_practice",
        requested_confidence=0.50,
        content_grade=9,  # Outside Grades 4-6 Intermediate Phase
    )
    assert not decision.is_authorized
    assert decision.status == "unsupported"
    assert "Intermediate Phase" in decision.reason


def test_evaluate_use_authorization_unknown_scope_and_to_dict():
    decision = evaluate_use_authorization(
        decision_scope="unknown_custom_scope",
        requested_confidence=0.50,
        content_grade=5,
    )
    assert not decision.is_authorized
    assert decision.status == "restricted"
    assert "unrecognized" in decision.reason

    d = decision.to_dict()
    assert d["is_authorized"] is False
    assert d["decision_scope"] == "unknown_custom_scope"
    assert d["status"] == "restricted"
    assert d["evidence_type"] == "synthetic_fixture"
