import math
import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.diagnostic_data_integrity import DiagnosticIntegrityError
from app.services.diagnostic_route_integrity import (
    assert_caps_ref_matches_session,
    served_items_from_snapshot,
    snapshot_caps_ref,
    validate_adaptive_diagnostic_response,
    _attr_or_key,
)
from app.services.diagnostic_safety import (
    DiagnosticItemValidation,
    DiagnosticItemValidator,
)
from app.services.diagnostic_scoring_snapshot import (
    diagnostic_item_from_response,
    diagnostic_response_snapshot,
    _value,
)
from app.services.diagnostic_session_integrity import (
    ServedDiagnosticItem,
    normalize_served_item,
    served_item_ids,
    validate_session_served_item_binding,
)


def test_diagnostic_route_integrity_complete():
    # 1. _attr_or_key with dict and object fallbacks (lines 11-18)
    d = {"k1": None, "k2": "val2"}
    assert _attr_or_key(d, "k1", "k2") == "val2"
    assert _attr_or_key(d, "nonexistent") is None

    class Obj:
        prop1 = "val1"
    assert _attr_or_key(Obj(), "nonexistent", "prop1") == "val1"
    assert _attr_or_key(Obj(), "nonexistent") is None

    # 2. assert_caps_ref_matches_session with None and mismatch (lines 27-32)
    assert_caps_ref_matches_session(submitted_caps_ref=None, session_caps_ref="4.M.1")
    assert_caps_ref_matches_session(submitted_caps_ref="4.M.1", session_caps_ref=None)
    with pytest.raises(DiagnosticIntegrityError, match="does not match session CAPS reference"):
        assert_caps_ref_matches_session(submitted_caps_ref="4.M.1", session_caps_ref="5.M.2")

    # 3. validate_adaptive_diagnostic_response empty served items (line 61)
    snapshot_empty = {"served_item_ids": [], "caps_ref": "4.M.1"}
    with pytest.raises(DiagnosticIntegrityError, match="no served items recorded"):
        validate_adaptive_diagnostic_response({"item_id": "i1"}, snapshot=snapshot_empty, session_id="s1")

    # 4. validate_adaptive_diagnostic_response success
    snapshot_valid = {"served_item_ids": ["i1", "i2"], "caps_ref": "4.M.1"}
    payload = {"item_id": "i1", "caps_ref": "4.M.1"}
    validate_adaptive_diagnostic_response(payload, snapshot=snapshot_valid, session_id="s1")


def test_diagnostic_safety_complete():
    validator = DiagnosticItemValidator()

    # 1. Pydantic validation failure (line 26)
    res_malformed = validator.validate_mapping({"completely": "invalid"})
    assert res_malformed.valid is False
    assert len(res_malformed.reasons) == 1

    # 2. Unaligned CAPS reference (line 30)
    item_bad_caps = {
        "item_id": "item-1",
        "subject": "Mathematics",
        "grade": 4,
        "topic": "Numbers",
        "skill": "Addition",
        "difficulty": 0.0,
        "discrimination": 1.0,
        "correct_answer": "A",
        "distractors": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "explanation": "Valid explanation",
        "caps_reference": "CAPS:v1:99.M.99",
        "review_status": "draft",
    }
    res_bad_caps = validator.validate_mapping(item_bad_caps)
    assert res_bad_caps.valid is False
    assert any("Unknown CAPS reference" in r for r in res_bad_caps.reasons)

    # 3. Duplicate distractors & missing explanation for approved item (lines 36, 38)
    # Note: CAPS:v1:MATH:grade4:numbers:add is a valid reference or we mock validate_caps_reference
    mock_caps_val = MagicMock()
    mock_caps_val.validate_caps_reference.return_value = MagicMock(caps_aligned=True, reason="")
    validator_with_mock_caps = DiagnosticItemValidator(caps_validator=mock_caps_val)

    item_dup = {
        "item_id": "item-2",
        "subject": "Mathematics",
        "grade": 4,
        "topic": "Numbers",
        "skill": "Addition",
        "difficulty": 0.0,
        "discrimination": 1.0,
        "correct_answer": "A",
        "distractors": {"A": "dup", "B": "dup", "C": "3", "D": "4"},
        "explanation": "  ",  # min_length=2 passes in pydantic, strip() is empty
        "caps_reference": "CAPS:v1:valid_ref",
        "review_status": "approved",
    }
    res_dup = validator_with_mock_caps.validate_mapping(item_dup)
    assert res_dup.valid is False
    assert any("distractors must be mutually distinct" in r for r in res_dup.reasons)
    assert any("approved items require an explanation" in r for r in res_dup.reasons)

    # 4. Out-of-bounds difficulty and discrimination (lines 31-34 via mocked contract)
    mock_contract = MagicMock(
        caps_reference="CAPS:v1:valid",
        difficulty=10.0,
        discrimination=-1.0,
        distractors={"A": "1", "B": "2", "C": "3", "D": "4"},
        review_status="draft",
        explanation="Valid",
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.diagnostic_safety.DiagnosticItemContract.model_validate", lambda x: mock_contract)
        res_bounds = validator_with_mock_caps.validate_mapping({})
        assert res_bounds.valid is False
        assert any("difficulty must be finite and between -4 and 4" in r for r in res_bounds.reasons)
        assert any("discrimination must be finite and between 0 and 4" in r for r in res_bounds.reasons)

    # 5. from_orm mapping (lines 41-57)
    orm_item = SimpleNamespace(
        id="orm-item-1",
        subject="Mathematics",
        grade=4,
        topic="Numbers",
        skill=None,
        b_param=0.5,
        a_param=1.2,
        correct_option="A",
        options={"A": "1", "B": "2", "C": "3", "D": "4"},
        explanation="Worked solution.",
        caps_reference="CAPS:v1:4.M.1",
        review_status="draft",
        misconception_tag="misconception_1",
    )
    res_orm = validator_with_mock_caps.from_orm(orm_item)
    assert isinstance(res_orm, DiagnosticItemValidation)



def test_diagnostic_scoring_snapshot_complete():
    # 1. _value helper with dict and object (line 20)
    d = {"k": "v"}
    assert _value(d, "k") == "v"
    assert _value(d, "missing", "default") == "default"

    # 2. diagnostic_response_snapshot with dict item
    snap = diagnostic_response_snapshot({"a_param": 1.5, "b_param": -0.5, "caps_ref": "4.M.1"}, item_id="item-x")
    assert snap["scoring"]["discrimination_a"] == 1.5
    assert snap["scoring"]["difficulty_b"] == -0.5

    # 3. diagnostic_item_from_response with fallback_item (lines 58-61)
    fallback = {"a_param": 1.8, "b_param": 0.2, "id": "fallback-id"}
    rebuilt_fallback = diagnostic_item_from_response({"item_id": "item-y"}, fallback_item=fallback)
    assert rebuilt_fallback.item_id == "item-y"
    assert rebuilt_fallback.discrimination_a == 1.8

    # 4. diagnostic_item_from_response without fallback_item (lines 62-71)
    rebuilt_default = diagnostic_item_from_response({"item_id": "item-z", "caps_ref": "4.M.1"})
    assert rebuilt_default.item_id == "item-z"
    assert rebuilt_default.discrimination_a == 1.0
    assert rebuilt_default.caps_ref == "4.M.1"


def test_diagnostic_session_integrity_complete():
    # 1. served_item_ids helper (lines 43-48)
    items = [
        {"item_id": "i1"},
        {"id": "i2"},
        {"no_id": "skip"},
    ]
    ids = served_item_ids(items)
    assert ids == {"i1", "i2"}

    # 2. validate_session_served_item_binding error branches (lines 76, 81, 86)
    served1 = ServedDiagnosticItem(item_id="item-1", session_id="s1", caps_topic="TopicA", caps_code="4.M.1")
    served_unsubmitted = ServedDiagnosticItem(item_id="item-unsubmitted", session_id="s1")
    served_list = [served1, served_unsubmitted]

    # Session ID mismatch (line 76)
    with pytest.raises(DiagnosticIntegrityError, match="belongs to session 's1', not 'other_session'"):
        validate_session_served_item_binding(
            {"item_id": "item-1"},
            served_items=served_list,
            session_id="other_session",
        )

    # CAPS topic mismatch (line 81)
    with pytest.raises(DiagnosticIntegrityError, match="belongs to CAPS topic 'TopicA', not 'OtherTopic'"):
        validate_session_served_item_binding(
            {"item_id": "item-1"},
            served_items=served_list,
            session_id="s1",
            caps_topic="OtherTopic",
        )

    # CAPS code mismatch (line 86)
    with pytest.raises(DiagnosticIntegrityError, match="belongs to CAPS code '4.M.1', not '9.M.9'"):
        validate_session_served_item_binding(
            {"item_id": "item-1"},
            served_items=served_list,
            session_id="s1",
            caps_code="9.M.9",
        )
