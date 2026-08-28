"""Comprehensive unit tests for AnswerKeyVerifier data models and CAPSTopicMapService path discovery."""
from __future__ import annotations

from pathlib import Path
import pytest

from app.modules.lessons.answer_key_verifier import (
    QuestionVerification,
    VerificationResult,
    PROMPT_TEMPLATE_VERSION,
)
from app.modules.lessons.caps_topic_map_service import (
    _discover_default_map_paths,
    CAPSTopicMapService,
)


class TestAnswerKeyVerifierDataModels:
    def test_question_verification_model(self):
        qv = QuestionVerification(
            question_id="q1",
            derived_answer="42",
            working="21 * 2 = 42",
            confidence=0.99,
            agrees_with_key=True,
            original_answer="42",
        )
        assert qv.question_id == "q1"
        assert qv.derived_answer == "42"
        assert qv.agrees_with_key is True

    def test_verification_result_to_dict(self):
        qv = QuestionVerification(
            question_id="q1",
            derived_answer="42",
            working="21 * 2 = 42",
            confidence=0.99,
            agrees_with_key=True,
            original_answer="42",
        )
        vr = VerificationResult(
            lesson_id="lesson_123",
            all_agree=True,
            verifications=[qv],
            disagreements=[],
            verification_model="llama-3.3-70b",
            verification_provider="groq",
        )
        data = vr.to_dict()
        assert data["lesson_id"] == "lesson_123"
        assert data["all_agree"] is True
        assert data["prompt_template_version"] == PROMPT_TEMPLATE_VERSION
        assert len(data["verifications"]) == 1
        assert data["verifications"][0]["derived_answer"] == "42"


class TestCAPSTopicMapServicePaths:
    def test_discover_default_map_paths(self):
        paths = _discover_default_map_paths()
        assert isinstance(paths, list)
        for p in paths:
            assert isinstance(p, Path)

    def test_topic_map_service_initialization(self):
        service = CAPSTopicMapService()
        assert service is not None
