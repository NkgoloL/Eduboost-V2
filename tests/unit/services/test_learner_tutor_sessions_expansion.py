import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.learner_tutor import (
    LearnerTutorService,
    _context_hash,
    _message_view,
    SYSTEM_PROMPT,
)
from app.models import Lesson
from app.models.tutor import TutorMessage, TutorSession


def test_system_prompt_and_helpers():
    assert "EduBoost learner tutor" in SYSTEM_PROMPT
    assert "plain text" in SYSTEM_PROMPT

    lesson = MagicMock(spec=Lesson)
    lesson.id = "les-1"
    lesson.subject = "Maths"
    lesson.topic = "Addition"
    lesson.content = "Lesson body content"

    h = _context_hash(lesson)
    assert len(h) == 64

    msg = MagicMock(spec=TutorMessage)
    msg.message_id = uuid.uuid4()
    msg.role = "assistant"
    msg.content = "Answer here"
    msg.safety_status = "safe"
    msg.quality_score = 0.95
    msg.provider = "mock"
    msg.created_at = None

    view = _message_view(msg)
    assert view["role"] == "assistant"
    assert view["content"] == "Answer here"
    assert view["quality_score"] == 0.95


@pytest.mark.asyncio
async def test_get_session_not_found():
    db = AsyncMock()
    db.get.return_value = None
    service = LearnerTutorService(db)

    with pytest.raises(Exception):
        await service.get_session(uuid.uuid4())
