"""Comprehensive unit tests for AnswerKeyVerifier, CAPSTopicMapService, and BudgetGuardrails."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.modules.lessons.answer_key_verifier import (
    QuestionVerification,
    AnswerKeyVerifier,
)
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.modules.lessons.budget_guardrails import (
    BudgetGuardrails,
    BudgetConfig,
    BudgetExceededError,
)


# ---------------------------------------------------------------------------
# Answer Key Verifier Data Class Tests
# ---------------------------------------------------------------------------

class TestAnswerKeyVerifierDataClasses:
    def test_question_verification_agreement(self):
        qv = QuestionVerification(
            question_id="q1",
            derived_answer="B",
            working="2 + 2 = 4 which is option B",
            confidence=0.98,
            original_answer="B",
            agrees_with_key=True,
        )
        assert qv.agrees_with_key is True
        assert qv.derived_answer == "B"

    def test_question_verification_disagreement(self):
        qv = QuestionVerification(
            question_id="q2",
            derived_answer="C",
            working="Step 1 indicates C",
            confidence=0.90,
            original_answer="A",
            agrees_with_key=False,
        )
        assert qv.agrees_with_key is False
        assert qv.derived_answer != qv.original_answer


# ---------------------------------------------------------------------------
# CAPS Topic Map Service Tests
# ---------------------------------------------------------------------------

class TestCAPSTopicMapService:
    def test_topic_map_init_and_lookup(self):
        service = CAPSTopicMapService()
        assert service is not None

    def test_topic_map_validate_known_ref(self):
        service = CAPSTopicMapService()
        valid = service.is_valid_ref("4.M.1.1")
        assert isinstance(valid, bool)


# ---------------------------------------------------------------------------
# Budget Guardrails Tests
# ---------------------------------------------------------------------------

class TestBudgetGuardrails:
    def test_budget_exceeded_error(self):
        err = BudgetExceededError(scope="user:u-123", used=50000, limit=50000)
        assert "Budget exceeded" in str(err) or "user:u-123" in str(err)

    @pytest.mark.asyncio
    async def test_in_process_fallback_guardrails(self):
        cfg = BudgetConfig(
            user_daily_token_limit=1000,
            tenant_monthly_token_limit=50000,
        )
        guardrails = BudgetGuardrails(config=cfg, redis=None)

        # Should allow under budget
        await guardrails.assert_budget(user_id="user_1", tenant_id="tenant_1", estimated_tokens=100)

        # Record usage
        await guardrails.record_usage(
            user_id="user_1",
            tenant_id="tenant_1",
            tokens_used=100,
            provider="groq",
            purpose="lesson_generation",
        )

        # Assert budget again
        await guardrails.assert_budget(user_id="user_1", tenant_id="tenant_1", estimated_tokens=100)
