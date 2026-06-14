"""
Phase 1 test fixtures.
All tests in this package use the DeterministicProvider —
no real LLM API calls are made.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.llm_provider import (
    DeterministicProvider,
    GenerationResult,
    ProviderRouter,
    TokenUsage,
)
from app.services.prompt_registry import PromptRegistry
from app.services.safety_filter import SafetyFilter
from app.services.content_validator import ContentValidator


# ---------------------------------------------------------------------------
# Sample valid payloads
# ---------------------------------------------------------------------------

VALID_DIAGNOSTIC_ITEM = {
    "question": "What is the value of 4 × 5?",
    "options": ["10", "15", "20", "25"],
    "correct_answer_index": 2,
    "explanation": "4 multiplied by 5 equals 20.",
    "bloom_level": "knowledge",
    "difficulty_band": "easy",
    "caps_ref": "4.M.1.1",
    "tags": ["multiplication"],
}

VALID_LESSON = {
    "title": "Understanding Multiplication: 4 × Table",
    "caps_ref": "4.M.1.1",
    "grade": 4,
    "subject_code": "MATHS",
    "language": "en",
    "learning_objectives": [
        "Recall multiples of 4 up to 4 × 12",
        "Solve word problems using multiplication by 4",
    ],
    "key_vocabulary": [
        {"term": "multiple", "definition": "A number that can be divided by another number without a remainder."},
    ],
    "body_markdown": (
        "# Multiplication by 4\n\n"
        "Multiplication is repeated addition. When we multiply by 4, we add a "
        "number to itself four times.\n\n"
        "For example: 4 × 3 = 3 + 3 + 3 + 3 = 12\n\n"
        "## The 4 times table\n\n"
        "| 4 × | = |\n|---|---|\n| 1 | 4 |\n| 2 | 8 |\n| 3 | 12 |\n"
    ),
    "worked_examples": [
        {
            "problem": "A farmer has 4 rows of orange trees with 6 trees in each row. How many trees are there?",
            "solution": "4 rows × 6 trees = 4 × 6 = 24",
            "answer": "24 orange trees",
        }
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def det_provider() -> DeterministicProvider:
    provider = DeterministicProvider()
    provider.register_default(json.dumps([VALID_DIAGNOSTIC_ITEM]))
    return provider


@pytest.fixture()
def provider_router(det_provider: DeterministicProvider) -> ProviderRouter:
    return ProviderRouter([det_provider])


@pytest.fixture()
def prompt_registry() -> PromptRegistry:
    return PromptRegistry.default()


@pytest.fixture()
def safety_filter() -> SafetyFilter:
    return SafetyFilter()


@pytest.fixture()
def validator() -> ContentValidator:
    return ContentValidator()


@pytest.fixture()
def mock_db() -> AsyncMock:
    """Minimal async DB session mock for unit tests."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


def make_generation_result(
    text: str = "{}",
    provider: str = "deterministic",
    model: str = "deterministic-v1",
    prompt_tokens: int = 100,
    completion_tokens: int = 200,
) -> GenerationResult:
    return GenerationResult(
        text=text,
        provider=provider,
        model=model,
        usage=TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=0.0,
        ),
        latency_ms=5.0,
    )
