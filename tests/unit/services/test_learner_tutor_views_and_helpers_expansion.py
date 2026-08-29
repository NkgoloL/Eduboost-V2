import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.tutor import TutorMessage
from app.models import Lesson
from app.services.learner_tutor import (
    _now,
    _context_hash,
    _message_view,
    LearnerTutorService,
)


def test_learner_tutor_helpers():
    now_dt = _now()
    assert now_dt.tzinfo is not None

    lesson = MagicMock(spec=Lesson)
    lesson.id = "lesson-1"
    lesson.subject = "mathematics"
    lesson.topic = "multiplication"
    lesson.content = "Multiplication table 2 to 10"

    h = _context_hash(lesson)
    assert isinstance(h, str)
    assert len(h) == 64

    msg = TutorMessage(
        session_id=uuid.uuid4(),
        client_message_id="msg-1",
        role="assistant",
        content="Here is a hint for question 1.",
        safety_status="safe",
        quality_score=0.95,
        provider="google",
    )
    view = _message_view(msg)
    assert view["role"] == "assistant"
    assert view["content"] == "Here is a hint for question 1."
    assert view["quality_score"] == 0.95


@pytest.mark.asyncio
async def test_learner_tutor_service_init():
    db = AsyncMock()
    service = LearnerTutorService(db)
    assert service.db == db
    assert service.ai_operations is not None
