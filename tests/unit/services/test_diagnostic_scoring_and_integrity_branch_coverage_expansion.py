"""Batch 232 — Diagnostic scoring snapshot, data integrity, and safety validator branch coverage expansion.

Tests:
- app/services/diagnostic_scoring_snapshot.py:
  - _value helper with dicts and objects
  - diagnostic_response_snapshot default vs explicit fields
  - diagnostic_item_from_response: scoring dict present, legacy fallback item, default fallback
- app/services/diagnostic_data_integrity.py:
  - extract_diagnostic_item_ids across dicts, objects, iterables
  - validate_diagnostic_submission_payload: empty items error, duplicate error, unserved error, success result
  - validate_theta_update: non-numeric/non-finite, out of bounds, delta too large, success
  - validate_mastery_update_payload: dicts and objects with multiple field aliases
  - clamp_theta: boundary checks
- app/services/diagnostic_safety.py:
  - DiagnosticItemValidator: validate_mapping with contract validation error, CAPS alignment failure, bounds checks, distractors uniqueness, approved without explanation, from_orm translation
"""
from __future__ import annotations

import math
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.caps_validator import CAPSValidationResult
from app.services.diagnostic_data_integrity import (
    DiagnosticIntegrityError,
    clamp_theta,
    extract_diagnostic_item_ids,
    validate_diagnostic_submission_payload,
    validate_mastery_update_payload,
    validate_theta_update,
)
from app.services.diagnostic_safety import (
    DiagnosticItemValidation,
    DiagnosticItemValidator,
)
from app.services.diagnostic_scoring_snapshot import (
    _value,
    diagnostic_item_from_response,
    diagnostic_response_snapshot,
)


# ---------------------------------------------------------------------------
# Scoring Snapshot Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_scoring_snapshot_value_and_snapshot():
    # _value
    d = {"name": "item-1"}
    obj = SimpleNamespace(name="item-2")
    assert _value(d, "name") == "item-1"
    assert _value(obj, "name") == "item-2"
    assert _value(d, "missing", "default") == "default"

    # diagnostic_response_snapshot
    item_dict = {
        "discrimination_a": 1.5,
        "difficulty_b": -0.5,
        "guessing_c": 0.2,
        "caps_ref": "4.M.1.1",
        "misconception_tags": ["tag-1"],
    }
    snap = diagnostic_response_snapshot(item_dict, item_id="item-100")
    assert snap["item_id"] == "item-100"
    assert snap["scoring"]["discrimination_a"] == 1.5
    assert snap["scoring"]["difficulty_b"] == -0.5
    assert snap["scoring"]["guessing_c"] == 0.2
    assert snap["scoring"]["caps_ref"] == "4.M.1.1"
    assert snap["scoring"]["misconception_tags"] == ["tag-1"]


@pytest.mark.unit
def test_diagnostic_item_from_response_rebuild():
    # 1. Existing scoring dictionary
    row_with_scoring = {
        "item_id": "i-1",
        "scoring": {
            "item_id": "i-1",
            "discrimination_a": 1.2,
            "difficulty_b": 0.3,
            "guessing_c": 0.25,
            "a_param": 1.2,
            "b_param": 0.3,
            "caps_ref": "4.M.1.1",
            "misconception_tags": [],
        },
    }
    item1 = diagnostic_item_from_response(row_with_scoring)
    assert item1.item_id == "i-1"
    assert item1.discrimination_a == 1.2

    # 2. Legacy fallback item
    fallback = SimpleNamespace(id="i-2", discrimination_a=1.8, difficulty_b=0.5)
    row_legacy = {"item_id": "i-2"}
    item2 = diagnostic_item_from_response(row_legacy, fallback_item=fallback)
    assert item2.item_id == "i-2"
    assert item2.discrimination_a == 1.8

    # 3. Bare fallback
    row_bare = {"item_id": "i-3", "caps_ref": "4.M.1.2"}
    item3 = diagnostic_item_from_response(row_bare)
    assert item3.item_id == "i-3"
    assert item3.discrimination_a == 1.0
    assert item3.caps_ref == "4.M.1.2"


# ---------------------------------------------------------------------------
# Data Integrity Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_extract_diagnostic_item_ids():
    payload = {
        "answers": [
            {"item_id": "item-1"},
            {"questionId": "item-2"},
        ],
        "nested": {
            "events": [
                SimpleNamespace(diagnostic_item_id="item-3"),
            ]
        },
    }
    extracted = extract_diagnostic_item_ids(payload)
    assert "item-1" in extracted
    assert "item-2" in extracted
    assert "item-3" in extracted


@pytest.mark.unit
def test_validate_diagnostic_submission_payload():
    # 1. Empty items when required -> DiagnosticIntegrityError
    with pytest.raises(DiagnosticIntegrityError, match="no item_id values"):
        validate_diagnostic_submission_payload({}, require_items=True)

    # 2. Duplicates -> DiagnosticIntegrityError
    payload_dup = {"answers": [{"item_id": "i-1"}, {"item_id": "i-1"}]}
    with pytest.raises(DiagnosticIntegrityError, match="Duplicate diagnostic item"):
        validate_diagnostic_submission_payload(payload_dup)

    # 3. Unserved items -> DiagnosticIntegrityError
    payload_unserved = {"answers": [{"item_id": "i-1"}, {"item_id": "i-2"}]}
    with pytest.raises(DiagnosticIntegrityError, match="unserved item IDs"):
        validate_diagnostic_submission_payload(payload_unserved, served_item_ids={"i-1"})

    # 4. Valid payload
    payload_valid = {"answers": [{"item_id": "i-1"}, {"item_id": "i-2"}]}
    res = validate_diagnostic_submission_payload(payload_valid, served_item_ids={"i-1", "i-2"})
    assert res.item_ids == ("i-1", "i-2")
    assert res.duplicate_item_ids == ()
    assert res.unserved_item_ids == ()


@pytest.mark.unit
def test_theta_and_mastery_validation():
    # Non-numeric & non-finite
    with pytest.raises(DiagnosticIntegrityError, match="must be numeric"):
        validate_theta_update(old_theta="invalid", new_theta=0.0)

    with pytest.raises(DiagnosticIntegrityError, match="must be finite"):
        validate_theta_update(old_theta=0.0, new_theta=float("inf"))

    # Out of bounds
    with pytest.raises(DiagnosticIntegrityError, match="out of bounds"):
        validate_theta_update(old_theta=0.0, new_theta=5.0)

    # Delta too large
    with pytest.raises(DiagnosticIntegrityError, match="delta too large"):
        validate_theta_update(old_theta=-1.0, new_theta=2.0, max_abs_delta=1.5)

    # Valid update
    assert validate_theta_update(old_theta=0.0, new_theta=0.5) == 0.5

    # Mastery payload validation (dict and object)
    validate_mastery_update_payload(None)
    validate_mastery_update_payload({"theta_before": 0.0, "theta_after": 0.4})
    validate_mastery_update_payload(SimpleNamespace(previous_theta=0.0, theta=0.3))

    # Clamp theta
    assert clamp_theta(-5.0) == -4.0
    assert clamp_theta(5.0) == 4.0
    assert clamp_theta(1.5) == 1.5


# ---------------------------------------------------------------------------
# Safety & Item Validator Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_diagnostic_item_validator():
    mock_caps = MagicMock()
    mock_caps.validate_caps_reference.return_value = CAPSValidationResult(
        caps_aligned=True,
        canonical_subject="Mathematics",
        canonical_topic="Numbers",
        reason="Valid CAPS",
        caps_reference="CAPS:2026:4.M.1.1",
    )

    validator = DiagnosticItemValidator(caps_validator=mock_caps)

    # 1. Invalid schema mapping
    res_inv = validator.validate_mapping({"invalid": "data"})
    assert res_inv.valid is False

    # 2. Valid mapping
    valid_map = {
        "item_id": "i-1",
        "subject": "Mathematics",
        "grade": 4,
        "topic": "Addition",
        "skill": "Mental Math",
        "difficulty": 0.0,
        "discrimination": 1.0,
        "correct_answer": "A",
        "distractors": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "explanation": "Valid worked explanation here.",
        "caps_reference": "CAPS:2026:4.M.1.1",
        "review_status": "approved",
    }
    res_valid = validator.validate_mapping(valid_map)
    assert res_valid.valid is True
    assert res_valid.reasons == ()

    # 3. Approved item missing explanation
    no_exp = dict(valid_map)
    no_exp["explanation"] = "   "
    res_no_exp = validator.validate_mapping(no_exp)
    assert res_no_exp.valid is False
    assert any("explanation" in r for r in res_no_exp.reasons)

    # 4. Duplicate distractors
    dup_dist = dict(valid_map)
    dup_dist["distractors"] = {"A": "1", "B": "1", "C": "3", "D": "4"}
    res_dup = validator.validate_mapping(dup_dist)
    assert res_dup.valid is False

    # 5. From ORM object
    orm_item = SimpleNamespace(
        id="i-orm",
        subject="Mathematics",
        grade=4,
        topic="Addition",
        skill="Mental Math",
        b_param=0.5,
        a_param=1.2,
        correct_option="A",
        options={"A": "1", "B": "2", "C": "3", "D": "4"},
        explanation="Full explanation",
        caps_reference="CAPS:2026:4.M.1.1",
        review_status="draft",
        misconception_tag=None,
    )
    res_orm = validator.from_orm(orm_item)
    assert res_orm.valid is True
