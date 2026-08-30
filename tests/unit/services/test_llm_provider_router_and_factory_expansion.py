"""Comprehensive unit tests for LLM provider abstractions and LLMContentGenerationProvider."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.llm_provider import (
    TokenUsage,
    GenerationResult,
    ProviderError,
    ProviderTimeoutError,
    ProviderRateLimitError,
    ProviderContentPolicyError,
    AllProvidersFailedError,
    CircuitBreaker,
    CircuitState,
)
from app.services.content_generation.providers.llm import (
    LLMContentGenerationProvider,
    _source_context,
    _json_items,
)
from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    LessonGenerationRequest,
    SourceContextChunk,
)


class TestLLMProviderResultTypes:
    def test_token_usage_and_telemetry(self):
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost_usd=0.0015,
        )
        res = GenerationResult(
            text='{"items": []}',
            provider="groq",
            model="llama-3.3-70b-versatile",
            usage=usage,
            latency_ms=250.4,
            request_id="req-123",
        )
        telem = res.to_telemetry_dict()
        assert telem["provider"] == "groq"
        assert telem["total_tokens"] == 150
        assert telem["request_id"] == "req-123"
        assert "text" not in telem

    def test_provider_errors_hierarchy(self):
        err = ProviderError("Timeout connecting to provider", provider="anthropic", retryable=True)
        assert err.provider == "anthropic"
        assert err.retryable is True

        timeout_err = ProviderTimeoutError("Request timed out", provider="groq")
        assert timeout_err.provider == "groq"

        rate_err = ProviderRateLimitError("Rate limit exceeded", provider="anthropic")
        assert rate_err.provider == "anthropic"

        all_err = AllProvidersFailedError("All configured providers failed")
        assert isinstance(all_err, Exception)

    def test_circuit_breaker_states(self):
        cb = CircuitBreaker(provider_name="groq", failure_threshold=3, recovery_timeout_seconds=10.0)
        assert cb.state == CircuitState.CLOSED
        assert cb.is_available() is True


class TestLLMContentGenerationProvider:
    def test_json_items_parser(self):
        assert _json_items('{"items": [{"id": 1}, {"id": 2}]}', key="items") == [{"id": 1}, {"id": 2}]
        assert _json_items('[{"id": 1}]', key="items") == [{"id": 1}]
        with pytest.raises(Exception):
            _json_items("invalid json", key="items")

    def test_source_context_formatter(self):
        chunk = SourceContextChunk(
            source_document_id="doc_1",
            source_chunk_id="chunk_1",
            text="Ordering and comparing whole numbers in Grade 4 mathematics.",
            document_status="approved",
        )
        ctx = _source_context([chunk])
        assert "chunk_1" in ctx
        assert "Ordering and comparing" in ctx

    @pytest.mark.asyncio
    async def test_generate_diagnostic_items(self):
        mock_router = AsyncMock()
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100)
        mock_router.generate.return_value = GenerationResult(
            text='{"items": [{"question_text": "What is 2+2?", "options": ["3", "4", "5"], "correct_answer": "4", "explanation": "2+2=4", "difficulty": 0.2, "cognitive_level": "knowledge"}]}',
            provider="mock",
            model="mock-model",
            usage=usage,
            latency_ms=100.0,
        )

        provider = LLMContentGenerationProvider(router=mock_router)
        chunk = SourceContextChunk(
            source_document_id="doc_1",
            source_chunk_id="chunk_1",
            text="Addition basics: 2 + 2 = 4.",
            document_status="approved",
        )
        req = DiagnosticGenerationRequest(
            scope_id="grade4_maths",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="mathematics",
            topic_title="Whole Numbers",
            language="en",
            required_count=5,
            approved_count=4,
            missing_count=1,
            source_chunks=[chunk],
        )

        items = await provider.generate_diagnostic_items(req)
        assert len(items) == 1
        assert items[0].question_text == "What is 2+2?"
        assert items[0].correct_answer == "4"
