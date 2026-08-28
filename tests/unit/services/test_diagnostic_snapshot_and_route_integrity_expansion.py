"""Comprehensive unit tests for diagnostic scoring snapshot pure functions."""
from __future__ import annotations

from types import SimpleNamespace
import pytest

from app.services.diagnostic_scoring_snapshot import (
    diagnostic_response_snapshot,
    diagnostic_item_from_response,
    SCORING_PARAMETER_FIELDS,
)


class TestDiagnosticScoringSnapshot:
    def test_scoring_parameter_fields_tuple(self):
        assert "discrimination_a" in SCORING_PARAMETER_FIELDS
        assert "difficulty_b" in SCORING_PARAMETER_FIELDS
        assert "guessing_c" in SCORING_PARAMETER_FIELDS
        assert "caps_ref" in SCORING_PARAMETER_FIELDS

    def test_diagnostic_response_snapshot_creation(self):
        item = SimpleNamespace(
            item_id="item_100",
            discrimination_a=1.25,
            difficulty_b=-0.2,
            guessing_c=0.20,
            caps_ref="4.M.1.1",
            misconception_tags=["fractions_basic"],
        )
        snap = diagnostic_response_snapshot(item, item_id="item_100")
        assert snap["item_id"] == "item_100"
        scoring = snap["scoring"]
        assert scoring["discrimination_a"] == 1.25
        assert scoring["difficulty_b"] == -0.2
        assert scoring["guessing_c"] == 0.20
        assert scoring["caps_ref"] == "4.M.1.1"
        assert scoring["misconception_tags"] == ["fractions_basic"]

    def test_diagnostic_item_from_response_with_scoring_dict(self):
        row = {
            "item_id": "item_100",
            "scoring": {
                "discrimination_a": 1.5,
                "difficulty_b": 0.5,
                "guessing_c": 0.25,
                "caps_ref": "4.M.1.1",
            },
        }
        rebuilt = diagnostic_item_from_response(row)
        assert rebuilt.discrimination_a == 1.5
        assert rebuilt.difficulty_b == 0.5

    def test_diagnostic_item_from_response_with_fallback_item(self):
        fallback = SimpleNamespace(item_id="item_fallback", discrimination_a=1.1, difficulty_b=0.1)
        row = {"item_id": "item_fallback"}
        rebuilt = diagnostic_item_from_response(row, fallback_item=fallback)
        assert rebuilt.discrimination_a == 1.1
