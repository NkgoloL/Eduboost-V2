"""Comprehensive unit tests for Extended Auth Router, Learner Tutor, Diagnostic Session Service, and DSR Workflows."""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from app.api_v2_routers.auth_extended import (
    _check_rate_limit,
    _reset_attempts,
    RESET_TTL_MIN,
    VERIFY_TTL_HR,
)
from app.services.learner_tutor import (
    LearnerTutorService,
    _context_hash,
    _message_view,
)
from app.models.tutor import TutorMessage
from app.services.diagnostic_session_service import (
    DiagnosticSessionService,
    DiagnosticSessionNotFoundError,
    _redis_key,
)
from app.modules.diagnostics.irt_engine import (
    DiagnosticSessionState,
    IRTEngine,
)


# ---------------------------------------------------------------------------
# Auth Extended Rate Limiter & Constants Tests
# ---------------------------------------------------------------------------

class TestAuthExtendedRateLimiter:
    def test_constants(self):
        assert RESET_TTL_MIN == 30
        assert VERIFY_TTL_HR == 24

    def test_rate_limit_allows_under_limit(self):
        ip = "192.168.1.100"
        _reset_attempts[ip].clear()
        for _ in range(4):
            _check_rate_limit(ip)
        assert len(_reset_attempts[ip]) == 4

    def test_rate_limit_blocks_at_max(self):
        ip = "192.168.1.101"
        _reset_attempts[ip].clear()
        for _ in range(5):
            _check_rate_limit(ip)
        with pytest.raises(HTTPException) as exc_info:
            _check_rate_limit(ip)
        assert exc_info.value.status_code == 429
        assert "Too many requests" in exc_info.value.detail


# ---------------------------------------------------------------------------
# Learner Tutor Helper & Service Tests
# ---------------------------------------------------------------------------

class TestLearnerTutorService:
    def test_context_hash_generation(self):
        lesson = MagicMock()
        lesson.id = uuid.uuid4()
        lesson.subject = "Mathematics"
        lesson.topic = "Fractions"
        lesson.content = "Lesson content on equivalent fractions."
        h = _context_hash(lesson)
        assert isinstance(h, str)
        assert len(h) == 64

    def test_message_view_structure(self):
        msg = TutorMessage(
            message_id=uuid.uuid4(),
            role="assistant",
            content="Here is a helpful hint for solving 1/2 + 1/4.",
            safety_status="passed",
            quality_score=0.95,
            provider="openai",
            created_at=datetime.now(timezone.utc),
        )
        view = _message_view(msg)
        assert view["message_id"] == msg.message_id
        assert view["role"] == "assistant"
        assert view["safety_status"] == "passed"
        assert view["quality_score"] == 0.95

    def test_learner_tutor_init(self):
        mock_db = AsyncMock()
        mock_router = MagicMock()
        tutor = LearnerTutorService(db=mock_db, provider_router=mock_router)
        assert tutor.db == mock_db


# ---------------------------------------------------------------------------
# Diagnostic Session Service Tests
# ---------------------------------------------------------------------------

class TestDiagnosticSessionService:
    def test_redis_key_format(self):
        sess_id = uuid.uuid4()
        key = _redis_key(sess_id)
        assert key == f"diagnostic:session:{sess_id}"

    def test_error_class(self):
        err = DiagnosticSessionNotFoundError("Session expired or missing")
        assert isinstance(err, Exception)

    @pytest.mark.asyncio
    async def test_session_lifecycle(self):
        mock_db = AsyncMock()
        mock_redis = AsyncMock()
        mock_item_bank = MagicMock()
        mock_engine = MagicMock()

        sess_id = uuid.uuid4()
        fake_state = DiagnosticSessionState(
            session_id=sess_id,
            learner_id=uuid.uuid4(),
            caps_ref="MATH.G4.NUM",
            theta=0.0,
            standard_error=1.0,
            responses=[],
            completed=False,
        )
        mock_engine.new_session.return_value = fake_state
        mock_redis.set.return_value = True

        svc = DiagnosticSessionService(
            db=mock_db,
            redis=mock_redis,
            item_bank_service=mock_item_bank,
            irt_engine=mock_engine,
        )

        state = await svc.create_session(
            learner_id=fake_state.learner_id,
            caps_ref="MATH.G4.NUM",
            prior_theta=0.0,
        )
        assert state.session_id == sess_id
        assert state.caps_ref == "MATH.G4.NUM"
        mock_redis.set.assert_called_once()
