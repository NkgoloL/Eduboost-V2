"""
Unit tests for:
  - app.services.batch_generation (GenerationTaskSpec dataclass)
  - app.services.learner_tutor (pure helper functions)
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.models.content_factory import ContentLayer
from app.services.batch_generation import GenerationTaskSpec
from app.services.learner_tutor import _context_hash, _message_view


# ---------------------------------------------------------------------------
# GenerationTaskSpec
# ---------------------------------------------------------------------------

class TestGenerationTaskSpec:
    def test_default_values(self):
        spec = GenerationTaskSpec(
            caps_ref="CAPS/MATH/GR4/NUMBER",
            content_layer=ContentLayer.LESSONS,
            content_type="lesson",
        )
        assert spec.count == 5
        assert spec.language == "en"
        assert spec.grade == 4
        assert spec.subject == "Mathematics"

    def test_custom_values(self):
        spec = GenerationTaskSpec(
            caps_ref="CAPS/SCI/GR7",
            content_layer=ContentLayer.LESSONS,
            content_type="explainer",
            count=10,
            language="af",
            grade=7,
            subject="Science",
        )
        assert spec.count == 10
        assert spec.language == "af"
        assert spec.grade == 7
        assert spec.subject == "Science"

    def test_frozen_dataclass(self):
        spec = GenerationTaskSpec(
            caps_ref="CAPS/MATH/GR4",
            content_layer=ContentLayer.LESSONS,
            content_type="lesson",
        )
        with pytest.raises((AttributeError, TypeError)):
            spec.count = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# learner_tutor pure helpers
# ---------------------------------------------------------------------------

class TestContextHash:
    def test_returns_deterministic_hash(self):
        lesson = MagicMock()
        lesson.id = "lesson-1"
        lesson.subject = "Math"
        lesson.topic = "Fractions"
        lesson.content = "Half of 8 is 4."

        h1 = _context_hash(lesson)
        h2 = _context_hash(lesson)
        assert h1 == h2
        assert len(h1) == 64  # sha256 hex digest

    def test_different_lessons_produce_different_hashes(self):
        lesson_a = MagicMock()
        lesson_a.id = "lesson-1"
        lesson_a.subject = "Math"
        lesson_a.topic = "Fractions"
        lesson_a.content = "Content A"

        lesson_b = MagicMock()
        lesson_b.id = "lesson-2"
        lesson_b.subject = "Math"
        lesson_b.topic = "Fractions"
        lesson_b.content = "Content B"

        assert _context_hash(lesson_a) != _context_hash(lesson_b)


class TestMessageView:
    def test_message_view_returns_expected_keys(self):
        msg = MagicMock()
        msg.message_id = "msg-001"
        msg.role = "assistant"
        msg.content = "Here is a hint."
        msg.safety_status = "safe"
        msg.quality_score = 0.95
        msg.provider = "deterministic"
        msg.created_at = datetime.now(timezone.utc)

        view = _message_view(msg)
        assert view["message_id"] == "msg-001"
        assert view["role"] == "assistant"
        assert view["content"] == "Here is a hint."
        assert view["safety_status"] == "safe"
        assert view["quality_score"] == 0.95
        assert view["provider"] == "deterministic"
        assert "created_at" in view

    def test_message_view_excludes_raw_model_fields(self):
        msg = MagicMock()
        msg.message_id = "msg-001"
        msg.role = "user"
        msg.content = "Help me"
        msg.safety_status = "safe"
        msg.quality_score = None
        msg.provider = None
        msg.created_at = None

        view = _message_view(msg)
        assert set(view.keys()) == {
            "message_id", "role", "content", "safety_status",
            "quality_score", "provider", "created_at"
        }
