"""Comprehensive unit tests for diagnostic router helpers and serialization."""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
import pytest

from app.api_v2_routers.diagnostics import (
    _subject_code,
    _option_payload,
    _serialise_item_bank_item,
)


class TestDiagnosticHelpers:
    def test_subject_code_mapping(self):
        assert _subject_code("mathematics") == "MATH"
        assert _subject_code("Math") == "MATH"
        assert _subject_code("english") == "ENG"
        assert _subject_code("natural sciences") == "NS"
        assert _subject_code("social science") == "SS"
        assert _subject_code("life skills") == "LIFE"
        assert _subject_code("CUSTOM_SUBJ") == "CUSTOM_SUBJ"
        assert _subject_code(None) == ""

    def test_option_payload_formats(self):
        # Empty
        assert _option_payload(None) == []
        assert _option_payload([]) == []

        # Dict format
        dict_opts = {"A": "First option", "B": "Second option"}
        assert _option_payload(dict_opts) == [
            {"key": "A", "label": "First option"},
            {"key": "B", "label": "Second option"},
        ]

        # List of strings
        list_str = ["Option 1", "Option 2"]
        assert _option_payload(list_str) == [
            {"key": "A", "label": "Option 1"},
            {"key": "B", "label": "Option 2"},
        ]

        # List of dicts
        list_dict = [
            {"key": "X", "label": "Choice X"},
            {"id": "Y", "text": "Choice Y"},
        ]
        assert _option_payload(list_dict) == [
            {"key": "X", "label": "Choice X"},
            {"key": "Y", "label": "Choice Y"},
        ]

    def test_serialise_item_bank_item(self):
        item = MagicMock()
        item.item_id = uuid.uuid4()
        item.stem = "What is 10 divided by 2?"
        item.options = ["2", "5", "10"]
        item.caps_ref = "4.M.1.2"
        item.grade = 4
        item.subject = "mathematics"
        item.cognitive_level = "understanding"
        item.difficulty = 0.3
        item.discrimination = 1.0

        res = _serialise_item_bank_item(item)
        assert res["item_id"] == str(item.item_id)
        assert res["question"] == "What is 10 divided by 2?"
        assert len(res["options"]) == 3
        assert res["options"][1]["label"] == "5"
        assert res["caps_ref"] == "4.M.1.2"
