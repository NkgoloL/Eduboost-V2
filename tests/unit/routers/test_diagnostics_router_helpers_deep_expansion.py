"""Comprehensive unit tests for diagnostic router serialization helpers and subject code mapping."""
from __future__ import annotations

from types import SimpleNamespace
import uuid
import pytest
from fastapi import HTTPException

from app.api_v2_routers.diagnostics import (
    _subject_code,
    _option_payload,
    _serialise_item_bank_item,
    _engine_item_from_item_bank,
    ReviewItemRequest,
    _require_item_bank_admin,
)


class TestDiagnosticRouterSerializationHelpers:
    def test_subject_code_mapping(self):
        assert _subject_code("mathematics") == "MATH"
        assert _subject_code("math") == "MATH"
        assert _subject_code("English") == "ENG"
        assert _subject_code("Natural Sciences") == "NS"
        assert _subject_code("social science") == "SS"
        assert _subject_code("Life Skills") == "LIFE"
        assert _subject_code("Custom Subject") == "Custom Subject"

    def test_option_payload_dict(self):
        options = {"A": "1/2", "B": "2/4", "C": "3/4"}
        payload = _option_payload(options)
        assert len(payload) == 3
        assert payload[0] == {"key": "A", "label": "1/2"}

    def test_option_payload_list_of_strings(self):
        options = ["First option", "Second option", "Third option"]
        payload = _option_payload(options)
        assert len(payload) == 3
        assert payload[0] == {"key": "A", "label": "First option"}
        assert payload[1] == {"key": "B", "label": "Second option"}
        assert payload[2] == {"key": "C", "label": "Third option"}

    def test_option_payload_list_of_dicts(self):
        options = [
            {"id": "opt_1", "text": "Option One"},
            {"key": "opt_2", "value": "Option Two"},
        ]
        payload = _option_payload(options)
        assert len(payload) == 2
        assert payload[0] == {"key": "opt_1", "label": "Option One"}
        assert payload[1] == {"key": "opt_2", "label": "Option Two"}

    def test_serialise_item_bank_item(self):
        item_id = uuid.uuid4()
        mock_item = SimpleNamespace(
            item_id=item_id,
            stem="What is 5 + 7?",
            options=["10", "11", "12", "13"],
            difficulty_b=0.2,
            discrimination_a=1.1,
            caps_ref="4.M.1.1",
            grade=4,
            subject="mathematics",
            topic="Numbers, Operations and Relationships",
            skill="Addition",
            review_status="approved",
        )
        serialised = _serialise_item_bank_item(mock_item)
        assert serialised["id"] == str(item_id)
        assert serialised["question"] == "What is 5 + 7?"
        assert serialised["subject"] == "MATH"
        assert serialised["topic"] == "Numbers, Operations and Relationships"
        assert len(serialised["options"]) == 4
        assert serialised["options"][2]["label"] == "12"

    def test_engine_item_from_item_bank(self):
        item_id = uuid.uuid4()
        mock_item = SimpleNamespace(
            item_id=item_id,
            grade=4,
            subject="mathematics",
            topic="Fractions",
            discrimination_a=1.2,
            difficulty_b=-0.5,
        )
        engine_item = _engine_item_from_item_bank(mock_item)
        assert engine_item.id == str(item_id)
        assert engine_item.grade == 4
        assert engine_item.subject == "MATH"
        assert engine_item.a_param == 1.2
        assert engine_item.b_param == -0.5

    def test_review_item_request_validation(self):
        req = ReviewItemRequest(review_status="approved", quality_score=0.95)
        assert req.review_status == "approved"
        assert req.quality_score == 0.95

        with pytest.raises(Exception):
            ReviewItemRequest(review_status="invalid_status")

    def test_require_item_bank_admin(self):
        admin_user = SimpleNamespace(is_admin=True)
        # Should not raise
        _require_item_bank_admin(admin_user)

        non_admin_user = SimpleNamespace(is_admin=False)
        with pytest.raises(HTTPException) as exc_info:
            _require_item_bank_admin(non_admin_user)
        assert exc_info.value.status_code == 403
