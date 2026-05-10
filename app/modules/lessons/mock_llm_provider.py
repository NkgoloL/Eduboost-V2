"""
EduBoost SA — Phase 2 (L2-07)
Deterministic Mock LLM Provider

Used in unit tests and CI golden-prompt tests in place of a live LLM gateway.

Features
--------
• Returns fixture lesson JSON that matches the full LessonCreate schema.
• Supports injecting specific validation failures for negative tests.
• Supports injecting answer-key disagreements for verifier tests.
• Zero latency / zero cost — no external network calls.
• Deterministic: same inputs → same outputs (no randomness).

Usage
-----
    from app.modules.lessons.mock_llm_provider import MockLLMProvider, MockMode

    # Happy-path (valid lesson)
    provider = MockLLMProvider(mode=MockMode.VALID_LESSON)
    response = await provider.complete(prompt="…")

    # Inject a specific validation failure
    provider = MockLLMProvider(
        mode=MockMode.INJECT_FAILURE,
        failure_field="worked_examples",
        failure_value=[],       # empty list → triggers R4
    )

    # Inject answer-key disagreement (verifier disagrees with key)
    provider = MockLLMProvider(mode=MockMode.ANSWER_KEY_DISAGREE)
"""

from __future__ import annotations

import copy
import json
import uuid
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Fixture data — canonical valid lesson for 4.M.1.1
# ---------------------------------------------------------------------------

_BASE_LESSON: dict[str, Any] = {
    "lesson_id": "00000000-0000-0000-0000-000000000001",
    "caps_ref": "4.M.1.1",
    "grade": 4,
    "subject": "Mathematics",
    "term": 1,
    "topic": "Whole Numbers",
    "subtopic": "Ordering and Comparing 4-digit Numbers",
    "learning_objectives": [
        "Compare and order 4-digit whole numbers using < > = symbols.",
        "Place 4-digit numbers on a number line.",
        "Explain the value of each digit using place value.",
    ],
    "explanation": (
        "A 4-digit number has thousands, hundreds, tens and ones. "
        "To compare two numbers, look at the thousands digit first. "
        "The number with the bigger thousands digit is larger. "
        "If the thousands are the same, look at the hundreds, then the tens, "
        "then the ones. For example, 3 450 is less than 3 720 because 4 < 7 "
        "in the hundreds column."
    ),
    "worked_examples": [
        {
            "question": "Which is bigger: 2 345 or 2 189?",
            "step_by_step_solution": (
                "Step 1: Both numbers start with 2 (thousands are equal).\n"
                "Step 2: Compare hundreds: 3 > 1.\n"
                "Step 3: So 2 345 > 2 189."
            ),
            "answer": "2 345 is bigger.",
        },
        {
            "question": "Order these numbers from smallest to largest: 4 210, 4 021, 4 120.",
            "step_by_step_solution": (
                "Step 1: Thousands are all 4 — compare hundreds: 2, 0, 1.\n"
                "Step 2: Order hundreds: 0 < 1 < 2.\n"
                "Step 3: So the order is 4 021, 4 120, 4 210."
            ),
            "answer": "4 021 < 4 120 < 4 210",
        },
    ],
    "practice_questions": [
        {
            "question_id": "q1",
            "question_text": "Which symbol completes this sentence? 5 302 ___ 5 230",
            "options": [
                {"label": "A", "text": "<"},
                {"label": "B", "text": ">"},
                {"label": "C", "text": "="},
                {"label": "D", "text": "≠"},
            ],
            "correct_answer": "B",
            "explanation": "5 302 > 5 230 because in the hundreds column 3 > 2.",
        },
        {
            "question_id": "q2",
            "question_text": "What is the value of the digit 7 in the number 3 741?",
            "options": [
                {"label": "A", "text": "7"},
                {"label": "B", "text": "70"},
                {"label": "C", "text": "700"},
                {"label": "D", "text": "7 000"},
            ],
            "correct_answer": "C",
            "explanation": "7 is in the hundreds column, so its value is 700.",
        },
        {
            "question_id": "q3",
            "question_text": "Order from largest to smallest: 1 009, 1 090, 1 900.",
            "options": [
                {"label": "A", "text": "1 009, 1 090, 1 900"},
                {"label": "B", "text": "1 900, 1 090, 1 009"},
                {"label": "C", "text": "1 090, 1 900, 1 009"},
                {"label": "D", "text": "1 009, 1 900, 1 090"},
            ],
            "correct_answer": "B",
            "explanation": "1 900 has the most hundreds so it is largest.",
        },
    ],
    "answer_key": {"q1": "B", "q2": "C", "q3": "B"},
    "remediation_hints": [
        {
            "misconception_tag": "digit_value_confusion",
            "hint_text": "Remember: the column a digit is in tells you its value. 7 in the hundreds column means 700, not just 7.",
            "example": "In 3 741, the 7 stands for 700.",
        }
    ],
    "difficulty_level": "on_level",
    "language_level": "Grade 4",
    "safety_classification": "safe",
    "pii_check_passed": True,
    "answer_key_verified": True,
    "quality_score": 0.88,
    "review_status": "ai_generated",
    "reviewer_id": None,
    "reviewed_at": None,
    "prompt_template_version": "lesson_generation_v1",
    "provider": "mock",
    "model_version": "mock_v1",
    "generation_latency_ms": 0,
    "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
}

# Verifier response — all agree
_BASE_VERIFIER_RESPONSE: list[dict[str, Any]] = [
    {"question_id": "q1", "derived_answer": "B", "working": "5 302 vs 5 230: hundreds 3 > 2, so 5 302 > 5 230 → B", "confidence": 0.99, "agrees_with_key": None},
    {"question_id": "q2", "derived_answer": "C", "working": "7 is in hundreds place → value is 700 → C", "confidence": 0.99, "agrees_with_key": None},
    {"question_id": "q3", "derived_answer": "B", "working": "1 900 > 1 090 > 1 009 → B", "confidence": 0.99, "agrees_with_key": None},
]

# Verifier response — one disagrees (for negative tests)
_DISAGREE_VERIFIER_RESPONSE: list[dict[str, Any]] = [
    {"question_id": "q1", "derived_answer": "A", "working": "Incorrect working shown", "confidence": 0.55, "agrees_with_key": None},
    {"question_id": "q2", "derived_answer": "C", "working": "Correct", "confidence": 0.99, "agrees_with_key": None},
    {"question_id": "q3", "derived_answer": "B", "working": "Correct", "confidence": 0.98, "agrees_with_key": None},
]


# ---------------------------------------------------------------------------
# Mock modes
# ---------------------------------------------------------------------------

class MockMode(Enum):
    VALID_LESSON = "valid_lesson"
    """Returns a perfectly valid lesson that passes all 8 validators."""

    INJECT_FAILURE = "inject_failure"
    """Returns a lesson with a specific field overridden to trigger a rule failure.
    Set ``failure_field`` and ``failure_value`` on the provider instance."""

    ANSWER_KEY_DISAGREE = "answer_key_disagree"
    """Verifier response has one answer that disagrees with the key."""

    PROVIDER_ERROR = "provider_error"
    """Simulates a gateway/provider error (raises LLMGatewayError)."""

    STATIC_FALLBACK = "static_fallback"
    """Returns the static fallback response (as if all providers failed)."""


# ---------------------------------------------------------------------------
# Mock provider
# ---------------------------------------------------------------------------

class MockLLMProvider:
    """Deterministic mock that replaces LLMGatewayV2 in tests.

    Parameters
    ----------
    mode:
        Controls what kind of response is returned.
    failure_field:
        When mode is INJECT_FAILURE, the lesson field to override.
    failure_value:
        The value to set for ``failure_field``.
    caps_ref:
        Override the caps_ref in the returned fixture lesson.
    """

    PROVIDER_NAME = "mock"
    MODEL_NAME = "mock_v1"

    def __init__(
        self,
        mode: MockMode = MockMode.VALID_LESSON,
        failure_field: str | None = None,
        failure_value: Any = None,
        caps_ref: str = "4.M.1.1",
    ) -> None:
        self.mode = mode
        self.failure_field = failure_field
        self.failure_value = failure_value
        self.caps_ref = caps_ref
        self._call_count = 0

    async def complete(
        self,
        prompt: str = "",
        system: str = "",
        **_kwargs: Any,
    ) -> dict[str, Any]:
        """Return a mock response matching the LLMGatewayV2 envelope."""
        from app.modules.lessons.llm_gateway_v2 import LLMGatewayError

        self._call_count += 1

        if self.mode is MockMode.PROVIDER_ERROR:
            raise LLMGatewayError("Mock provider error (injected for test)")

        if self.mode is MockMode.STATIC_FALLBACK:
            return {
                "content": "Service temporarily unavailable.",
                "provider": "static",
                "model": "static_fallback_v1",
                "used_fallback": True,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "latency_ms": 0,
            }

        # Determine which fixture to return based on prompt heuristics
        is_verifier_call = "agrees_with_key" in prompt or "VERIFICATION" in (system or "").upper()

        if is_verifier_call:
            return self._verifier_response()

        return self._lesson_response()

    def _lesson_response(self) -> dict[str, Any]:
        lesson = copy.deepcopy(_BASE_LESSON)
        lesson["lesson_id"] = str(uuid.uuid4())
        lesson["caps_ref"] = self.caps_ref

        if self.mode is MockMode.INJECT_FAILURE and self.failure_field:
            lesson[self.failure_field] = self.failure_value

        content = json.dumps(lesson)
        return {
            "content": content,
            "provider": self.PROVIDER_NAME,
            "model": self.MODEL_NAME,
            "used_fallback": False,
            "prompt_tokens": 100,
            "completion_tokens": len(content) // 4,
            "total_tokens": 100 + len(content) // 4,
            "latency_ms": 0,
        }

    def _verifier_response(self) -> dict[str, Any]:
        if self.mode is MockMode.ANSWER_KEY_DISAGREE:
            payload = copy.deepcopy(_DISAGREE_VERIFIER_RESPONSE)
        else:
            payload = copy.deepcopy(_BASE_VERIFIER_RESPONSE)

        content = json.dumps(payload)
        return {
            "content": content,
            "provider": self.PROVIDER_NAME,
            "model": self.MODEL_NAME,
            "used_fallback": False,
            "prompt_tokens": 80,
            "completion_tokens": len(content) // 4,
            "total_tokens": 80 + len(content) // 4,
            "latency_ms": 0,
        }

    @property
    def call_count(self) -> int:
        """Number of times ``complete()`` has been called on this instance."""
        return self._call_count
