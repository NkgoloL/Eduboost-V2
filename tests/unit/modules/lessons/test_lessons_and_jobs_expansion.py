"""Comprehensive unit tests for MockLLMProvider and Job Dependency Factory."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.modules.lessons.mock_llm_provider import (
    MockLLMProvider,
    MockMode,
)
from app.services.job_dependency_factory import (
    _import_symbol,
    _session_factory,
    _construct,
    build_consent_service_for_job,
)


# ---------------------------------------------------------------------------
# Mock LLM Provider Tests
# ---------------------------------------------------------------------------

class TestMockLLMProvider:
    @pytest.mark.asyncio
    async def test_mock_valid_lesson_mode(self):
        provider = MockLLMProvider(mode=MockMode.VALID_LESSON)
        resp = await provider.complete(prompt="Generate Grade 4 lesson on whole numbers")
        assert resp is not None
        assert "content" in resp
        data = json.loads(resp["content"])
        assert data["grade"] == 4
        assert data["subject"] == "Mathematics"

    @pytest.mark.asyncio
    async def test_mock_inject_failure_mode(self):
        provider = MockLLMProvider(
            mode=MockMode.INJECT_FAILURE,
            failure_field="worked_examples",
            failure_value=[],
        )
        resp = await provider.complete(prompt="Generate lesson with missing examples")
        data = json.loads(resp["content"])
        assert data["worked_examples"] == []

    @pytest.mark.asyncio
    async def test_mock_answer_key_disagree_mode(self):
        provider = MockLLMProvider(mode=MockMode.ANSWER_KEY_DISAGREE)
        resp = await provider.complete(prompt="Generate lesson with disagreeing answer key")
        data = json.loads(resp["content"])
        assert "practice_questions" in data


# ---------------------------------------------------------------------------
# Job Dependency Factory Tests
# ---------------------------------------------------------------------------

class TestJobDependencyFactory:
    def test_import_symbol_valid(self):
        sym = _import_symbol("app.services.job_dependency_factory._construct")
        assert sym is _construct

    def test_import_symbol_invalid(self):
        sym = _import_symbol("app.non_existent_module.FakeClass")
        assert sym is None

    def test_session_factory(self):
        factory = _session_factory()
        assert callable(factory)

    def test_construct_helper(self):
        class Dummy:
            def __init__(self, val: int = 10):
                self.val = val

        obj = _construct(Dummy, 42)
        assert obj.val == 42
        obj2 = _construct(Dummy)
        assert obj2.val == 10

    def test_build_consent_service(self):
        mock_session = AsyncMock()
        service = build_consent_service_for_job(mock_session)
        assert service is not None
