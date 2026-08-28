"""Comprehensive unit tests for answer key verifier and CAPS topic map service."""
from __future__ import annotations

from pathlib import Path
import pytest

from app.modules.lessons.answer_key_verifier import (
    QuestionVerification,
    VerificationResult,
    _normalise_answer,
    _answers_agree,
)
from app.modules.lessons.caps_topic_map_service import (
    CAPSTopicMapService,
    _discover_default_map_paths,
)


class TestAnswerKeyVerifierHelpers:
    def test_normalise_answer_integers_and_floats(self):
        assert _normalise_answer(" 4.0 ") == "4"
        assert _normalise_answer("005") == "5"
        assert _normalise_answer("3.14159") == "3.14159"
        assert _normalise_answer("4,5") == "4.5"
        assert _normalise_answer("  Option A  ") == "option a"

    def test_answers_agree_comparisons(self):
        assert _answers_agree("4.0", "4") is True
        assert _answers_agree("4,0", "4.0") is True
        assert _answers_agree("Option B", "option b") is True
        assert _answers_agree("42", "43") is False

    def test_verification_result_to_dict(self):
        qv = QuestionVerification(
            question_id="q1",
            derived_answer="4",
            working="2+2=4",
            confidence=0.99,
            agrees_with_key=True,
            original_answer="4",
        )
        res = VerificationResult(
            lesson_id="lesson-xyz",
            all_agree=True,
            verifications=[qv],
            verification_model="test-model",
            verification_provider="test-provider",
        )
        data = res.to_dict()
        assert data["lesson_id"] == "lesson-xyz"
        assert data["all_agree"] is True
        assert len(data["verifications"]) == 1
        assert data["verifications"][0]["agrees_with_key"] is True


class TestCAPSTopicMapService:
    def test_discover_default_map_paths(self):
        paths = _discover_default_map_paths()
        assert isinstance(paths, list)
        for p in paths:
            assert isinstance(p, Path)

    def test_topic_map_service_singleton_or_instantiation(self):
        service = CAPSTopicMapService()
        assert service is not None
