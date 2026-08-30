"""Batch 202: Unit tests for diagnostic_scoring_snapshot and diagnostic_session_integrity."""
import pytest
from types import SimpleNamespace

from app.services.diagnostic_scoring_snapshot import (
    SCORING_PARAMETER_FIELDS,
    diagnostic_item_from_response,
    diagnostic_response_snapshot,
)
from app.services.diagnostic_session_integrity import (
    DiagnosticIntegrityError,
    ServedDiagnosticItem,
    normalize_served_item,
    served_item_ids,
    validate_session_served_item_binding,
)


# ─────────────────────────────────────────────
# diagnostic_response_snapshot
# ─────────────────────────────────────────────


class TestDiagnosticResponseSnapshot:
    def test_from_dict_with_all_fields(self):
        item = {
            "discrimination_a": 1.2,
            "difficulty_b": -0.5,
            "guessing_c": 0.2,
            "caps_ref": "CAPS:MATH:G7:FRACTIONS",
            "misconception_tags": ["fraction_confusion"],
        }
        result = diagnostic_response_snapshot(item, item_id="item-001")
        assert result["item_id"] == "item-001"
        scoring = result["scoring"]
        assert scoring["discrimination_a"] == 1.2
        assert scoring["difficulty_b"] == -0.5
        assert scoring["guessing_c"] == 0.2
        assert scoring["caps_ref"] == "CAPS:MATH:G7:FRACTIONS"
        assert scoring["misconception_tags"] == ["fraction_confusion"]

    def test_from_dict_with_a_param_b_param(self):
        item = {"a_param": 0.9, "b_param": 1.1}
        result = diagnostic_response_snapshot(item, item_id="item-002")
        scoring = result["scoring"]
        assert scoring["a_param"] == 0.9
        assert scoring["b_param"] == 1.1
        assert scoring["discrimination_a"] == 0.9  # falls back from a_param

    def test_from_object_with_attributes(self):
        item = SimpleNamespace(discrimination_a=1.5, difficulty_b=0.3, guessing_c=0.25, caps_ref=None, misconception_tags=[])
        result = diagnostic_response_snapshot(item, item_id="item-003")
        assert result["scoring"]["discrimination_a"] == 1.5

    def test_defaults_applied_when_none(self):
        result = diagnostic_response_snapshot({}, item_id="item-empty")
        scoring = result["scoring"]
        assert scoring["discrimination_a"] == 1.0  # default
        assert scoring["difficulty_b"] == 0.0
        assert scoring["guessing_c"] == 0.25

    def test_item_id_cast_to_string(self):
        result = diagnostic_response_snapshot({}, item_id=12345)
        assert result["item_id"] == "12345"

    def test_scoring_parameter_fields_constant(self):
        assert isinstance(SCORING_PARAMETER_FIELDS, tuple)
        assert "a_param" in SCORING_PARAMETER_FIELDS
        assert "b_param" in SCORING_PARAMETER_FIELDS


# ─────────────────────────────────────────────
# diagnostic_item_from_response
# ─────────────────────────────────────────────


class TestDiagnosticItemFromResponse:
    def test_from_scoring_dict(self):
        row = {
            "item_id": "item-X",
            "scoring": {
                "item_id": "item-X",
                "discrimination_a": 1.1,
                "difficulty_b": 0.5,
                "guessing_c": 0.25,
                "a_param": 1.1,
                "b_param": 0.5,
                "caps_ref": "CAPS:MATH",
                "misconception_tags": [],
            }
        }
        ns = diagnostic_item_from_response(row)
        assert ns.discrimination_a == 1.1
        assert ns.difficulty_b == 0.5

    def test_from_legacy_item_key(self):
        row = {
            "item_id": "item-legacy",
            "item": {
                "item_id": "item-legacy",
                "discrimination_a": 0.8,
                "difficulty_b": -1.0,
                "guessing_c": 0.25,
                "a_param": 0.8,
                "b_param": -1.0,
                "caps_ref": None,
                "misconception_tags": [],
            }
        }
        ns = diagnostic_item_from_response(row)
        assert ns.discrimination_a == 0.8

    def test_fallback_item_used_when_no_scoring(self):
        row = {"item_id": "item-Y"}
        fallback = SimpleNamespace(item_id="item-Y", a_param=1.3, b_param=-0.2, discrimination_a=1.3, difficulty_b=-0.2, guessing_c=0.25, caps_ref=None, misconception_tags=[])
        ns = diagnostic_item_from_response(row, fallback_item=fallback)
        assert ns.item_id == "item-Y"

    def test_no_scoring_no_fallback_returns_defaults(self):
        row = {"item_id": "item-Z"}
        ns = diagnostic_item_from_response(row)
        assert ns.discrimination_a == 1.0
        assert ns.difficulty_b == 0.0
        assert ns.guessing_c == 0.25
        assert ns.caps_ref is None


# ─────────────────────────────────────────────
# normalize_served_item and served_item_ids
# ─────────────────────────────────────────────


class TestNormalizeServedItem:
    def test_from_dict(self):
        item = {"item_id": "item-1", "session_id": "sess-1", "caps_topic": "fractions", "caps_code": "CAPS:MATH"}
        normalized = normalize_served_item(item)
        assert normalized.item_id == "item-1"
        assert normalized.session_id == "sess-1"
        assert normalized.caps_topic == "fractions"
        assert normalized.caps_code == "CAPS:MATH"

    def test_from_object_attrs(self):
        item = SimpleNamespace(item_id="item-2", session_id="sess-2", caps_topic=None, caps_code=None)
        normalized = normalize_served_item(item)
        assert normalized.item_id == "item-2"

    def test_camel_case_item_id(self):
        item = {"itemId": "item-3"}
        normalized = normalize_served_item(item)
        assert normalized.item_id == "item-3"

    def test_missing_item_id_returns_none(self):
        normalized = normalize_served_item({})
        assert normalized.item_id is None


class TestServedItemIds:
    def test_extracts_ids_from_list(self):
        items = [{"item_id": "A"}, {"item_id": "B"}]
        ids = served_item_ids(items)
        assert ids == {"A", "B"}

    def test_skips_none_item_ids(self):
        items = [{"item_id": None}, {"item_id": "C"}]
        ids = served_item_ids(items)
        assert ids == {"C"}

    def test_empty_list_returns_empty_set(self):
        assert served_item_ids([]) == set()


# ─────────────────────────────────────────────
# validate_session_served_item_binding
# ─────────────────────────────────────────────


class TestValidateSessionServedItemBinding:
    def test_valid_submission_passes(self):
        payload = [{"item_id": "item-1"}]
        served = [{"item_id": "item-1", "session_id": "sess-1"}]
        # Should not raise
        validate_session_served_item_binding(payload, served_items=served, session_id="sess-1")

    def test_wrong_session_raises(self):
        payload = [{"item_id": "item-1"}]
        served = [{"item_id": "item-1", "session_id": "sess-A"}]
        with pytest.raises(DiagnosticIntegrityError, match="session"):
            validate_session_served_item_binding(payload, served_items=served, session_id="sess-B")

    def test_wrong_caps_topic_raises(self):
        payload = [{"item_id": "item-2"}]
        served = [{"item_id": "item-2", "caps_topic": "fractions"}]
        with pytest.raises(DiagnosticIntegrityError, match="CAPS topic"):
            validate_session_served_item_binding(payload, served_items=served, caps_topic="algebra")

    def test_wrong_caps_code_raises(self):
        payload = [{"item_id": "item-3"}]
        served = [{"item_id": "item-3", "caps_code": "CAPS:MATH"}]
        with pytest.raises(DiagnosticIntegrityError, match="CAPS code"):
            validate_session_served_item_binding(payload, served_items=served, caps_code="CAPS:SCIENCE")

    def test_unserved_item_raises(self):
        payload = [{"item_id": "item-unserved"}]
        served = [{"item_id": "item-1"}]
        with pytest.raises(DiagnosticIntegrityError):
            validate_session_served_item_binding(payload, served_items=served)
