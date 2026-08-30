"""Comprehensive unit tests for Parent and Tutor router schemas and session models."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
import pytest

from app.domain.tutor_schemas import (
    TutorSessionCreate,
    TutorQuestion,
    TutorMessageView,
    TutorSessionView,
    TutorReply,
    TutorCancelResponse,
)
from app.domain.schemas import (
    ParentDashboardLearner,
    ParentDashboardResponse,
)


class TestTutorSchemas:
    def test_tutor_session_create_valid(self):
        req = TutorSessionCreate(
            learner_id="learner_123",
            lesson_id="lesson_456",
            language="en",
        )
        assert req.learner_id == "learner_123"
        assert req.lesson_id == "lesson_456"
        assert req.language == "en"

    def test_tutor_session_create_invalid_language(self):
        with pytest.raises(Exception):
            TutorSessionCreate(
                learner_id="learner_123",
                lesson_id="lesson_456",
                language="english",  # Needs 2-letter code
            )

    def test_tutor_question_valid(self):
        q = TutorQuestion(
            text="Can you explain step 2 again?",
            client_message_id="msg_client_001",
        )
        assert q.text == "Can you explain step 2 again?"
        assert q.client_message_id == "msg_client_001"

    def test_tutor_session_view(self):
        sid = uuid.uuid4()
        mid = uuid.uuid4()
        now = datetime.now(UTC)

        msg = TutorMessageView(
            message_id=mid,
            role="assistant",
            content="Sure! In step 2, we find the common denominator.",
            safety_status="safe",
            quality_score=0.95,
            provider="groq",
            created_at=now,
        )

        view = TutorSessionView(
            session_id=sid,
            learner_id="learner_123",
            lesson_id="lesson_456",
            language="en",
            status="active",
            message_count=1,
            escalation_count=0,
            created_at=now,
            last_activity_at=now,
            messages=[msg],
        )
        assert view.session_id == sid
        assert len(view.messages) == 1
        assert view.messages[0].quality_score == 0.95


class TestParentDashboardSchemas:
    def test_parent_dashboard_response(self):
        lid = uuid.uuid4()
        gid = uuid.uuid4()
        now = datetime.now(UTC)

        learner_dash = ParentDashboardLearner(
            learner_id=lid,
            display_name="Thabo",
            grade_level="4",
            archetype="visual",
            irt_theta=0.5,
            lessons_this_week=3,
            active_knowledge_gaps=1,
            last_lesson_at=now,
        )

        dash = ParentDashboardResponse(
            guardian_id=gid,
            learners=[learner_dash],
            total_lessons_generated=12,
            subscription_tier="free",
        )
        assert len(dash.learners) == 1
        assert dash.learners[0].display_name == "Thabo"
        assert dash.total_lessons_generated == 12
        assert dash.subscription_tier == "free"
