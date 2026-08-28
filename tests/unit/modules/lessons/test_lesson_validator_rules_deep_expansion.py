"""Comprehensive unit tests for LessonValidator individual rules and readability calculations."""
from __future__ import annotations

from types import SimpleNamespace
import pytest

from app.modules.lessons.lesson_validator import LessonValidator


class TestLessonValidatorRules:
    def test_estimate_flesch_kincaid_grade_empty(self):
        score = LessonValidator._estimate_flesch_kincaid_grade("")
        assert score == 0.0

        score_spaces = LessonValidator._estimate_flesch_kincaid_grade("   ")
        assert score_spaces == 0.0

    def test_estimate_flesch_kincaid_grade_simple(self):
        text = "The cat sat on the mat. It was a big red mat."
        score = LessonValidator._estimate_flesch_kincaid_grade(text)
        assert 1.0 <= score <= 6.0

    def test_estimate_flesch_kincaid_grade_complex(self):
        text = "The fundamental mathematical properties of fractions encompass proportional relationships and equivalence transformations."
        score = LessonValidator._estimate_flesch_kincaid_grade(text)
        assert score > 6.0

    def test_rule_min_worked_examples(self):
        lesson_1 = SimpleNamespace(worked_examples=["ex1"])
        assert LessonValidator._rule_min_worked_examples(lesson_1) is False

        lesson_2 = SimpleNamespace(worked_examples=["ex1", "ex2"])
        assert LessonValidator._rule_min_worked_examples(lesson_2) is True

    def test_rule_min_practice_questions(self):
        lesson_2 = SimpleNamespace(practice_questions=["q1", "q2"])
        assert LessonValidator._rule_min_practice_questions(lesson_2) is False

        lesson_3 = SimpleNamespace(practice_questions=["q1", "q2", "q3"])
        assert LessonValidator._rule_min_practice_questions(lesson_3) is True
