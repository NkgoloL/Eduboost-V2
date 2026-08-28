"""Comprehensive unit tests for LearnerTutorService and helpers."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.learner_tutor import (
    LearnerTutorService,
    _context_hash,
    _message_view,
    _now,
    SYSTEM_PROMPT,
)
from app.models.tutor import TutorMessage, TutorSession
from app.models import Lesson


class TestTutorHelpers:
    def test_system_prompt_safety(self):
        assert "plain text" in SYSTEM_PROMPT.lower()
        assert "south africa" in SYSTEM_PROMPT.lower()

    def test_now_utc(self):
        dt = _now()
        assert dt is not None

    def test_context_hash(self):
        lesson = MagicMock(spec=Lesson)
        lesson.id = uuid.uuid4()
        lesson.subject = "mathematics"
        lesson.topic = "multiplication"
        lesson.content = "Multiplication is repeated addition."
        h = _context_hash(lesson)
        assert isinstance(h, str)
        assert len(h) == 64

    def test_message_view(self):
        msg = MagicMock(spec=TutorMessage)
        msg.message_id = uuid.uuid4()
        msg.role = "assistant"
        msg.content = "Think about 4 groups of 5."
        msg.safety_status = "safe"
        msg.quality_score = 0.95
        msg.provider = "groq"
        msg.created_at = _now()

        view = _message_view(msg)
        assert view["role"] == "assistant"
        assert view["content"] == "Think about 4 groups of 5."
        assert view["safety_status"] == "safe"
        assert view["quality_score"] == 0.95


class TestLearnerTutorService:
    def test_service_init(self):
        mock_db = AsyncMock()
        service = LearnerTutorService(db=mock_db)
        assert service.db == mock_db
