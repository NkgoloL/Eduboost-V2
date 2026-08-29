import json
import pytest
from unittest.mock import AsyncMock, patch

from app.core.llm import (
    _cache_key,
    active_provider_label,
    ExecutiveService,
    QuotaExceededError,
)
from app.core.judiciary import LessonPayload


def test_cache_key_generation():
    key = _cache_key(5, "maths", "fractions", "en", "visual")
    assert key.startswith("lesson_cache:")
    assert len(key) > 20


def test_active_provider_label():
    label = active_provider_label()
    assert label in {"", "auto", "google", "groq", "anthropic", "fallback", "mock", "local_hf"}


def test_executive_call_mock():
    svc = ExecutiveService()
    raw = svc._call_mock("Topic: Whole Numbers | Grade 4", operation="test")
    parsed = json.loads(raw)
    assert "Whole Numbers" in parsed["title"]
    assert parsed["safety_classification"] == "safe"


def test_executive_build_lesson_prompt():
    svc = ExecutiveService()
    prompt = svc._build_lesson_prompt(
        grade=4,
        subject="Mathematics",
        topic="Numbers",
        language="en",
        archetype="visual",
        requested_topic="Numbers",
    )
    assert "Grade 4" in prompt
    assert "Mathematics" in prompt
    assert "visual" in prompt
