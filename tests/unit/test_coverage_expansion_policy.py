"""
Unit tests for app.core.policy (JudiciaryService, ConstitutionalViolation).
"""
from __future__ import annotations

import json

import pytest

from app.core.policy import (
    ConstitutionalViolation,
    JudiciaryService,
    PolicyService,
    PolicyViolation,
)


def make_lesson_json(**overrides) -> str:
    base = {
        "title": "Introduction to Fractions",
        "introduction": "A fraction is a part of a whole.",
        "main_content": "When we divide a whole into equal parts, each part is a fraction.",
        "worked_example": "If we cut a pizza into 4 slices, each slice is 1/4.",
        "practice_question": "What fraction is one slice if a pizza has 8 slices?",
        "answer": "1/8",
        "cultural_hook": "Think of sharing a traditional South African koeksister.",
    }
    base.update(overrides)
    return json.dumps(base)


def make_study_plan_json(**overrides) -> str:
    base = {
        "week_label": "Week 1",
        "daily_topics": ["Fractions intro", "Unit fractions"],
        "priority_gaps": ["Division"],
    }
    base.update(overrides)
    return json.dumps(base)


def make_diagnostic_json(**overrides) -> str:
    base = {
        "summary": "The learner needs improvement in fraction operations.",
        "encouragement": "Keep practising — you are making great progress!",
    }
    base.update(overrides)
    return json.dumps(base)


class TestJudiciaryService:
    def setup_method(self):
        self.svc = JudiciaryService()

    # --- stamp_lesson ---

    def test_stamp_lesson_valid(self):
        payload = self.svc.stamp_lesson(make_lesson_json())
        assert payload.title == "Introduction to Fractions"

    def test_stamp_lesson_strips_markdown_fences(self):
        raw = f"```json\n{make_lesson_json()}\n```"
        payload = self.svc.stamp_lesson(raw)
        assert payload.answer == "1/8"

    def test_stamp_lesson_blocked_word_raises(self):
        with pytest.raises(ConstitutionalViolation, match="policy violation"):
            self.svc.stamp_lesson(make_lesson_json(title="Introduction to violence"))

    def test_stamp_lesson_empty_json_raises(self):
        with pytest.raises(ConstitutionalViolation):
            self.svc.stamp_lesson("```json\n\n```")

    def test_stamp_lesson_invalid_schema_raises(self):
        with pytest.raises(ConstitutionalViolation, match="schema violation"):
            self.svc.stamp_lesson('{"title": "short"}')

    def test_stamp_lesson_placeholder_answer_raises(self):
        with pytest.raises(ConstitutionalViolation, match="placeholder"):
            self.svc.stamp_lesson(make_lesson_json(answer="TBD"))

    def test_stamp_lesson_empty_answer_raises(self):
        with pytest.raises(ConstitutionalViolation):
            self.svc.stamp_lesson(make_lesson_json(answer=" "))

    # --- stamp_study_plan ---

    def test_stamp_study_plan_valid(self):
        payload = self.svc.stamp_study_plan(make_study_plan_json())
        assert payload.week_label == "Week 1"

    def test_stamp_study_plan_invalid_raises(self):
        with pytest.raises(ConstitutionalViolation):
            self.svc.stamp_study_plan('{"bad": "data"}')

    # --- stamp_diagnostic_feedback ---

    def test_stamp_diagnostic_feedback_valid(self):
        payload = self.svc.stamp_diagnostic_feedback(make_diagnostic_json())
        assert "fraction" in payload.summary.lower()

    def test_stamp_diagnostic_feedback_invalid_raises(self):
        with pytest.raises(ConstitutionalViolation):
            self.svc.stamp_diagnostic_feedback('{"no_summary": true}')


class TestBackwardCompatibleAliases:
    def test_policy_violation_is_constitutional_violation(self):
        assert PolicyViolation is ConstitutionalViolation

    def test_policy_service_is_judiciary_service(self):
        assert PolicyService is JudiciaryService

    def test_can_raise_as_policy_violation(self):
        with pytest.raises(PolicyViolation):
            raise ConstitutionalViolation("test")
