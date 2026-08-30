"""Batch 201: Unit tests for diagnostic_data_integrity and diagnostic_safety services."""
import math
import pytest

from app.services.diagnostic_data_integrity import (
    DiagnosticIntegrityError,
    DiagnosticSubmissionIntegrityResult,
    clamp_theta,
    extract_diagnostic_item_ids,
    validate_diagnostic_submission_payload,
    validate_mastery_update_payload,
    validate_theta_update,
)


# ─────────────────────────────────────────────
# extract_diagnostic_item_ids
# ─────────────────────────────────────────────


class TestExtractDiagnosticItemIds:
    def test_extracts_from_dict_with_item_id(self):
        payload = {"item_id": "item-001", "answer": "A"}
        result = extract_diagnostic_item_ids(payload)
        assert "item-001" in result

    def test_extracts_from_dict_with_question_id(self):
        payload = {"question_id": "q-123", "answer": "B"}
        result = extract_diagnostic_item_ids(payload)
        assert "q-123" in result

    def test_extracts_from_list_of_dicts(self):
        payload = [
            {"item_id": "item-001"},
            {"item_id": "item-002"},
        ]
        result = extract_diagnostic_item_ids(payload)
        assert "item-001" in result
        assert "item-002" in result

    def test_extracts_from_nested_responses(self):
        payload = {"responses": [{"item_id": "item-A"}, {"item_id": "item-B"}]}
        result = extract_diagnostic_item_ids(payload)
        assert "item-A" in result
        assert "item-B" in result

    def test_none_returns_empty(self):
        result = extract_diagnostic_item_ids(None)
        assert result == []

    def test_string_returns_empty(self):
        result = extract_diagnostic_item_ids("not a dict")
        assert result == []

    def test_object_with_item_id_attribute(self):
        class Item:
            item_id = "attr-item-1"
        result = extract_diagnostic_item_ids(Item())
        assert "attr-item-1" in result

    def test_none_item_id_skipped(self):
        payload = {"item_id": None, "other": "value"}
        result = extract_diagnostic_item_ids(payload)
        assert None not in result

    def test_camel_case_item_id(self):
        payload = {"itemId": "camel-001"}
        result = extract_diagnostic_item_ids(payload)
        assert "camel-001" in result


# ─────────────────────────────────────────────
# validate_diagnostic_submission_payload
# ─────────────────────────────────────────────


class TestValidateDiagnosticSubmissionPayload:
    def test_valid_payload_returns_result(self):
        payload = [{"item_id": "item-1"}, {"item_id": "item-2"}]
        result = validate_diagnostic_submission_payload(payload, served_item_ids={"item-1", "item-2"})
        assert isinstance(result, DiagnosticSubmissionIntegrityResult)
        assert "item-1" in result.item_ids
        assert result.duplicate_item_ids == ()
        assert result.unserved_item_ids == ()

    def test_empty_payload_with_require_items_raises(self):
        with pytest.raises(DiagnosticIntegrityError, match="no item_id"):
            validate_diagnostic_submission_payload({}, require_items=True)

    def test_empty_payload_without_require_items_ok(self):
        result = validate_diagnostic_submission_payload({}, require_items=False)
        assert result.item_ids == ()

    def test_duplicate_item_ids_raises(self):
        payload = [{"item_id": "item-1"}, {"item_id": "item-1"}]
        with pytest.raises(DiagnosticIntegrityError, match="Duplicate"):
            validate_diagnostic_submission_payload(payload)

    def test_unserved_item_raises(self):
        payload = [{"item_id": "item-99"}]
        with pytest.raises(DiagnosticIntegrityError, match="unserved"):
            validate_diagnostic_submission_payload(payload, served_item_ids={"item-1"})

    def test_no_served_ids_no_unserved_check(self):
        payload = [{"item_id": "item-X"}]
        result = validate_diagnostic_submission_payload(payload, served_item_ids=None)
        assert "item-X" in result.item_ids
        assert result.unserved_item_ids == ()


# ─────────────────────────────────────────────
# validate_theta_update
# ─────────────────────────────────────────────


class TestValidateThetaUpdate:
    def test_valid_theta_update(self):
        result = validate_theta_update(old_theta=0.0, new_theta=1.5)
        assert result == 1.5

    def test_new_theta_out_of_bounds_raises(self):
        with pytest.raises(DiagnosticIntegrityError, match="out of bounds"):
            validate_theta_update(old_theta=0.0, new_theta=5.0)

    def test_negative_out_of_bounds_raises(self):
        with pytest.raises(DiagnosticIntegrityError, match="out of bounds"):
            validate_theta_update(old_theta=0.0, new_theta=-5.0)

    def test_large_delta_raises(self):
        with pytest.raises(DiagnosticIntegrityError, match="delta too large"):
            validate_theta_update(old_theta=0.0, new_theta=3.0, max_abs_delta=2.5)

    def test_non_numeric_old_theta_raises(self):
        with pytest.raises(DiagnosticIntegrityError, match="must be numeric"):
            validate_theta_update(old_theta="not_a_number", new_theta=0.0)

    def test_non_finite_new_theta_raises(self):
        with pytest.raises(DiagnosticIntegrityError, match="must be finite"):
            validate_theta_update(old_theta=0.0, new_theta=float("inf"))

    def test_boundary_theta_accepted(self):
        # new_theta=4.0 is at the boundary but delta from 2.0 is 2.0 < 2.5
        result = validate_theta_update(old_theta=2.0, new_theta=4.0)
        assert result == 4.0
        result2 = validate_theta_update(old_theta=-2.0, new_theta=-4.0)
        assert result2 == -4.0


# ─────────────────────────────────────────────
# validate_mastery_update_payload
# ─────────────────────────────────────────────


class TestValidateMasteryUpdatePayload:
    def test_none_payload_returns_without_error(self):
        # Should not raise
        validate_mastery_update_payload(None)

    def test_dict_payload_with_theta_validates(self):
        validate_mastery_update_payload({"old_theta": 0.0, "new_theta": 1.0})

    def test_dict_payload_with_invalid_theta_raises(self):
        with pytest.raises(DiagnosticIntegrityError):
            validate_mastery_update_payload({"old_theta": 0.0, "new_theta": 10.0})

    def test_dict_payload_missing_old_theta_skips_check(self):
        # Only new_theta, no old_theta — should not raise
        validate_mastery_update_payload({"new_theta": 1.5})

    def test_object_payload_with_attrs(self):
        class Payload:
            old_theta = 0.0
            new_theta = 1.5
        validate_mastery_update_payload(Payload())


# ─────────────────────────────────────────────
# clamp_theta
# ─────────────────────────────────────────────


class TestClampTheta:
    def test_clamps_above_max(self):
        assert clamp_theta(10.0) == 4.0

    def test_clamps_below_min(self):
        assert clamp_theta(-10.0) == -4.0

    def test_within_bounds_returned_as_is(self):
        assert clamp_theta(2.5) == 2.5

    def test_non_numeric_raises(self):
        with pytest.raises(DiagnosticIntegrityError, match="must be numeric"):
            clamp_theta("not_a_number")

    def test_nan_raises(self):
        with pytest.raises(DiagnosticIntegrityError, match="must be finite"):
            clamp_theta(float("nan"))


# ─────────────────────────────────────────────
# DiagnosticIntegrityError
# ─────────────────────────────────────────────


class TestDiagnosticIntegrityError:
    def test_is_value_error_subclass(self):
        err = DiagnosticIntegrityError("test")
        assert isinstance(err, ValueError)

    def test_message_preserved(self):
        err = DiagnosticIntegrityError("custom message")
        assert "custom message" in str(err)
