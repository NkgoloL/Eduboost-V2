import math
from unittest.mock import MagicMock
import pytest

from app.services.diagnostic_data_integrity import (
    DiagnosticIntegrityError,
    clamp_theta,
    extract_diagnostic_item_ids,
    validate_diagnostic_submission_payload,
    validate_mastery_update_payload,
    validate_theta_update,
)
from app.services.diagnostic_route_integrity import (
    assert_caps_ref_matches_session,
    served_items_from_snapshot,
    snapshot_caps_ref,
    validate_adaptive_diagnostic_response,
)
from app.services.diagnostic_safety import (
    DiagnosticItemValidation,
    DiagnosticItemValidator,
)
from app.services.diagnostic_scoring_snapshot import (
    diagnostic_item_from_response,
    diagnostic_response_snapshot,
)
from app.services.diagnostic_session_integrity import (
    ServedDiagnosticItem,
    normalize_served_item,
    served_item_ids,
    validate_session_served_item_binding,
)
from app.services.diagnostic_transactional_response import (
    DiagnosticTransactionError,
    DiagnosticTransactionInput,
    TransactionalDiagnosticResponseService,
)


def test_diagnostic_safety_expansion():
    validator = DiagnosticItemValidator()

    # Test from_orm
    orm_item = MagicMock()
    orm_item.id = "item_123"
    orm_item.subject = "Mathematics"
    orm_item.grade = 4
    orm_item.topic = "Fractions"
    orm_item.skill = None
    orm_item.b_param = 0.5
    orm_item.a_param = 1.2
    orm_item.correct_option = "A"
    orm_item.options = {"A": "1/2", "B": "1/3", "C": "1/4", "D": "1/5"}
    orm_item.explanation = "Worked solution"
    orm_item.caps_reference = "CAPS.MATH.G4.NUM.01"
    orm_item.review_status = "approved"
    orm_item.misconception_tag = "tag1"

    res = validator.from_orm(orm_item)
    assert isinstance(res, DiagnosticItemValidation)

    # Test invalid cases in validate_mapping:
    # 1. Invalid difficulty
    bad_diff = {
        "item_id": "i1", "subject": "Math", "grade": 4, "topic": "T", "skill": "S",
        "difficulty": 10.0, "discrimination": 1.0, "correct_answer": "A",
        "distractors": {"A": "1", "B": "2", "C": "3", "D": "4"}, "explanation": "exp",
        "caps_reference": "CAPS.MATH.G4.NUM.01", "review_status": "draft"
    }
    assert not validator.validate_mapping(bad_diff).valid

    # 2. Invalid discrimination
    bad_disc = dict(bad_diff)
    bad_disc["difficulty"] = 0.0
    bad_disc["discrimination"] = -1.0
    assert not validator.validate_mapping(bad_disc).valid

    # 3. Duplicate distractors
    bad_opts = dict(bad_diff)
    bad_opts["difficulty"] = 0.0
    bad_opts["distractors"] = {"A": "1", "B": "1", "C": "3", "D": "4"}
    assert not validator.validate_mapping(bad_opts).valid

    # 4. Approved without explanation
    bad_exp = dict(bad_diff)
    bad_exp["difficulty"] = 0.0
    bad_exp["review_status"] = "approved"
    bad_exp["explanation"] = "   "
    assert not validator.validate_mapping(bad_exp).valid


def test_diagnostic_scoring_snapshot_expansion():
    # 1. _value on dict vs object
    d_item = {"discrimination_a": 1.5, "b_param": -0.2, "caps_ref": "CAPS.01"}
    snap = diagnostic_response_snapshot(d_item, item_id="item_dict")
    assert snap["scoring"]["discrimination_a"] == 1.5
    assert snap["scoring"]["b_param"] == -0.2

    # 2. diagnostic_item_from_response with fallback_item
    row_no_scoring = {"item_id": "it_1"}
    rebuilt = diagnostic_item_from_response(row_no_scoring, fallback_item=d_item)
    assert rebuilt.discrimination_a == 1.5

    # 3. diagnostic_item_from_response without fallback_item
    rebuilt_default = diagnostic_item_from_response({"item_id": "it_default"})
    assert rebuilt_default.discrimination_a == 1.0
    assert rebuilt_default.difficulty_b == 0.0


def test_diagnostic_route_integrity_expansion():
    from types import SimpleNamespace

    # 1. snapshot_caps_ref and _attr_or_key on dict and obj
    assert snapshot_caps_ref({"caps_ref": "C1"}) == "C1"
    assert snapshot_caps_ref({"capsRef": "C2"}) == "C2"
    assert snapshot_caps_ref(SimpleNamespace(caps_code="C3")) == "C3"


    # 2. assert_caps_ref_matches_session mismatch vs None
    assert_caps_ref_matches_session(submitted_caps_ref=None, session_caps_ref="C1")
    assert_caps_ref_matches_session(submitted_caps_ref="C1", session_caps_ref=None)
    with pytest.raises(DiagnosticIntegrityError):
        assert_caps_ref_matches_session(submitted_caps_ref="C1", session_caps_ref="C2")

    # 3. served_items_from_snapshot
    items = served_items_from_snapshot({"served_item_ids": ["item_a", "item_b"], "caps_ref": "C1"}, session_id="s1")
    assert len(items) == 2
    assert items[0]["session_id"] == "s1"

    # 4. validate_adaptive_diagnostic_response empty served items error
    with pytest.raises(DiagnosticIntegrityError, match="Diagnostic session has no served items recorded"):
        validate_adaptive_diagnostic_response({"item_id": "x"}, snapshot={"served_item_ids": []}, session_id="s1")



def test_diagnostic_session_integrity_expansion():
    # 1. served_item_ids
    items = [
        {"item_id": "i1", "session_id": "s1"},
        {"id": "i2", "session_id": "s1"},
    ]
    ids = served_item_ids(items)
    assert "i1" in ids and "i2" in ids

    # 2. validate_session_served_item_binding errors for session_id, caps_topic, caps_code mismatch
    served = [
        {"item_id": "i1", "session_id": "s1", "caps_topic": "T1", "caps_code": "C1"},
    ]
    # Mismatched session_id
    with pytest.raises(DiagnosticIntegrityError, match="belongs to session"):
        validate_session_served_item_binding({"item_id": "i1"}, served_items=served, session_id="s2")

    # Mismatched caps_topic
    with pytest.raises(DiagnosticIntegrityError, match="belongs to CAPS topic"):
        validate_session_served_item_binding({"item_id": "i1"}, served_items=served, caps_topic="T2")

    # Mismatched caps_code
    with pytest.raises(DiagnosticIntegrityError, match="belongs to CAPS code"):
        validate_session_served_item_binding({"item_id": "i1"}, served_items=served, caps_code="C2")


def test_diagnostic_data_integrity_expansion():
    from types import SimpleNamespace

    # 1. extract_diagnostic_item_ids on edge cases
    assert extract_diagnostic_item_ids(None) == []
    assert extract_diagnostic_item_ids("string_literal") == []
    obj = SimpleNamespace(item_id="mock_id", responses=None)
    assert extract_diagnostic_item_ids(obj) == ["mock_id"]


    # 2. validate_diagnostic_submission_payload empty require_items
    with pytest.raises(DiagnosticIntegrityError, match="contains no item_id"):
        validate_diagnostic_submission_payload({}, require_items=True)

    # 3. validate_theta_update non-numeric or non-finite or delta too large
    with pytest.raises(DiagnosticIntegrityError, match="must be numeric"):
        validate_theta_update(old_theta="bad", new_theta=0.0)

    with pytest.raises(DiagnosticIntegrityError, match="must be finite"):
        validate_theta_update(old_theta=float("inf"), new_theta=0.0)

    with pytest.raises(DiagnosticIntegrityError, match="delta too large"):
        validate_theta_update(old_theta=0.0, new_theta=3.0, max_abs_delta=2.0)

    # 4. validate_mastery_update_payload with dict and obj shapes
    validate_mastery_update_payload(None)
    validate_mastery_update_payload({"old_theta": 0.0, "new_theta": 0.5})
    obj_payload = MagicMock(old_theta=0.1, new_theta=0.2)
    validate_mastery_update_payload(obj_payload)

    # 5. clamp_theta
    assert clamp_theta(5.0) == 4.0
    assert clamp_theta(-5.0) == -4.0
    assert clamp_theta(0.5) == 0.5

    # 6. extract_diagnostic_item_ids cycle handling
    cycle_dict: dict = {"item_id": "root_id"}
    cycle_dict["self"] = cycle_dict
    assert extract_diagnostic_item_ids(cycle_dict) == ["root_id"]


def test_diagnostic_service_shims():
    import app.services.diagnostic as diag_shim
    assert hasattr(diag_shim, "DiagnosticEngine")
    assert hasattr(diag_shim, "p_correct")
    assert hasattr(diag_shim, "update_theta_mle")

