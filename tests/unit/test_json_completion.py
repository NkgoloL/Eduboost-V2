"""tests/unit/test_json_completion.py
Unit tests for JsonCompletionGateway and helpers (no network calls).
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.llm.json_completion import (
    JsonCompletionError,
    JsonCompletionGateway,
    parse_json_response,
)


@pytest.mark.unit
def test_parse_json_response_accepts_fenced_markdown():
    raw = """
    ```json
    {"a": 1, "b": 2}
    ```
    """.strip()
    parsed = parse_json_response(raw)
    assert parsed == {"a": 1, "b": 2}


@pytest.mark.unit
def test_parse_json_response_raises_on_invalid_json():
    with pytest.raises(JsonCompletionError, match="not valid JSON"):
        parse_json_response("{" )


@pytest.mark.unit
async def test_complete_uses_mock_provider_when_configured(monkeypatch):
    # Arrange settings
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "mock", raising=False)

    gw = JsonCompletionGateway()
    resp = await gw.complete(prompt="give me correct_answer")
    assert resp.provider == "mock"
    assert "correct_answer" in resp.content


@pytest.mark.unit
async def test_mock_returns_empty_dict_for_generic_prompt(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "mock", raising=False)

    gw = JsonCompletionGateway()
    resp = await gw.complete(prompt="generic prompt")
    assert resp.provider == "mock"
    assert resp.content == "{}"


@pytest.mark.unit
async def test_mock_returns_answer_key_for_lowercase_prompt(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "mock", raising=False)

    gw = JsonCompletionGateway()
    resp = await gw.complete(prompt="give me answer key")
    assert resp.provider == "mock"
    assert "correct_answer" in resp.content


@pytest.mark.unit
async def test_google_path_success(monkeypatch):
    from app.core import config
    # minimal viable settings
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)

    payload = {
        "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 34},
        "candidates": [
            {"content": {"parts": [{"text": "{\"ok\": true}"}]}}
        ],
    }

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi", system="s", max_tokens=512, temperature=0.5, operation="test_op")

        assert resp.provider == "google"
        assert resp.model == "gemini-pro"
        assert resp.content == "{\"ok\": true}"
        assert resp.prompt_tokens == 12
        assert resp.completion_tokens == 34
        mock_record.assert_called_once()
        # Verify the request was made with correct parameters
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        json_payload = call_args[1]["json"]
        assert json_payload["generationConfig"]["responseMimeType"] == "application/json"
        assert json_payload["generationConfig"]["maxOutputTokens"] == 512
        assert json_payload["generationConfig"]["temperature"] == 0.5


@pytest.mark.unit
async def test_google_handles_missing_usage_metadata(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)

    payload = {
        "candidates": [
            {"content": {"parts": [{"text": "{\"ok\": true}"}]}}
        ],
    }

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi")

        assert resp.provider == "google"
        assert resp.prompt_tokens == 0
        assert resp.completion_tokens == 0
        mock_record.assert_called_once()


@pytest.mark.unit
async def test_google_handles_partial_usage_metadata(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)

    payload = {
        "usageMetadata": {},
        "candidates": [
            {"content": {"parts": [{"text": "{\"ok\": true}"}]}}
        ],
    }

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi")

        assert resp.provider == "google"
        assert resp.prompt_tokens == 0
        assert resp.completion_tokens == 0
        mock_record.assert_called_once()


@pytest.mark.unit
async def test_google_requires_api_key(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "", raising=False)

    gw = JsonCompletionGateway()
    with pytest.raises(JsonCompletionError, match="Google Gemini API key not configured"):
        await gw.complete(prompt="p")


@pytest.mark.unit
async def test_google_raises_on_no_candidates(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)

    payload = {"usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 34}, "candidates": []}

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        gw = JsonCompletionGateway()
        with pytest.raises(JsonCompletionError, match="returned no candidates"):
            await gw.complete(prompt="hi")


@pytest.mark.unit
async def test_google_raises_on_empty_content(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)

    payload = {
        "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 34},
        "candidates": [{"content": {"parts": [{"text": ""}]}}],
    }

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        gw = JsonCompletionGateway()
        with pytest.raises(JsonCompletionError, match="returned an empty response"):
            await gw.complete(prompt="hi")


@pytest.mark.unit
async def test_google_raises_on_http_error(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Server error", request=MagicMock(), response=MagicMock())
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        gw = JsonCompletionGateway()
        with pytest.raises(httpx.HTTPStatusError):
            await gw.complete(prompt="hi")


@pytest.mark.unit
async def test_groq_requires_api_key(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "groq", raising=False)
    monkeypatch.setattr(config.settings, "GROQ_API_KEY", "", raising=False)

    gw = JsonCompletionGateway()
    with pytest.raises(JsonCompletionError, match="Groq API key not configured"):
        await gw.complete(prompt="p")


@pytest.mark.unit
async def test_anthropic_requires_api_key(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "anthropic", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_API_KEY", "", raising=False)

    gw = JsonCompletionGateway()
    with pytest.raises(JsonCompletionError, match="Anthropic API key not configured"):
        await gw.complete(prompt="p")


@pytest.mark.unit
async def test_fallback_collects_errors_when_no_provider_configured(monkeypatch):
    from app.core import config
    # Ensure explicit provider is unset; emulate no keys so fallback will gather none
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "unknown", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "", raising=False)
    monkeypatch.setattr(config.settings, "GROQ_API_KEY", "", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_API_KEY", "", raising=False)

    gw = JsonCompletionGateway()
    with pytest.raises(JsonCompletionError, match="No JSON LLM provider succeeded"):
        await gw.complete(prompt="p")


@pytest.mark.unit
async def test_groq_path_success(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "groq", raising=False)
    monkeypatch.setattr(config.settings, "GROQ_API_KEY", "k", raising=False)

    mock_completion = MagicMock()
    mock_completion.usage.prompt_tokens = 10
    mock_completion.usage.completion_tokens = 20
    mock_completion.choices[0].message.content = '{"result": "ok"}'

    with patch("app.services.llm.json_completion.AsyncGroq") as mock_groq_cls, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        mock_groq = MagicMock()
        mock_groq_cls.return_value = mock_groq
        mock_groq.chat.completions.create = AsyncMock(return_value=mock_completion)

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi", system="s", max_tokens=256, temperature=0.3, operation="groq_test")

        assert resp.provider == "groq"
        assert resp.model == "llama3-70b-8192"  # default from getattr
        assert resp.content == '{"result": "ok"}'
        assert resp.prompt_tokens == 10
        assert resp.completion_tokens == 20
        mock_record.assert_called_once()
        # Verify the call was made with correct parameters
        call_args = mock_groq.chat.completions.create.call_args
        assert call_args[1]["model"] == "llama3-70b-8192"
        assert call_args[1]["max_tokens"] == 256
        assert call_args[1]["temperature"] == 0.3
        assert call_args[1]["response_format"] == {"type": "json_object"}


@pytest.mark.unit
async def test_groq_handles_missing_usage(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "groq", raising=False)
    monkeypatch.setattr(config.settings, "GROQ_API_KEY", "k", raising=False)

    mock_completion = MagicMock()
    mock_completion.usage = None
    mock_completion.choices[0].message.content = '{"result": "ok"}'

    with patch("app.services.llm.json_completion.AsyncGroq") as mock_groq_cls, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        mock_groq = MagicMock()
        mock_groq_cls.return_value = mock_groq
        mock_groq.chat.completions.create = AsyncMock(return_value=mock_completion)

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi")

        assert resp.provider == "groq"
        assert resp.prompt_tokens == 0
        assert resp.completion_tokens == 0
        mock_record.assert_called_once()


@pytest.mark.unit
async def test_anthropic_path_success(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "anthropic", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_MODEL", "claude-3-opus", raising=False)

    mock_message = MagicMock()
    mock_message.usage.input_tokens = 15
    mock_message.usage.output_tokens = 25
    mock_block = MagicMock()
    mock_block.text = '{"data": "value"}'
    mock_message.content = [mock_block]

    with patch("app.services.llm.json_completion.anthropic.AsyncAnthropic") as mock_anthropic_cls, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        mock_anthropic = MagicMock()
        mock_anthropic_cls.return_value = mock_anthropic
        mock_anthropic.messages.create = AsyncMock(return_value=mock_message)

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi", system="s", max_tokens=128, temperature=0.7, operation="anthropic_test")

        assert resp.provider == "anthropic"
        assert resp.model == "claude-3-opus"
        assert resp.content == '{"data": "value"}'
        assert resp.prompt_tokens == 15
        assert resp.completion_tokens == 25
        mock_record.assert_called_once()
        # Verify the call was made with correct parameters
        call_args = mock_anthropic.messages.create.call_args
        assert call_args[1]["model"] == "claude-3-opus"
        assert call_args[1]["max_tokens"] == 128
        assert call_args[1]["temperature"] == 0.7
        assert call_args[1]["system"] == "s"


@pytest.mark.unit
async def test_anthropic_handles_empty_content(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "anthropic", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_MODEL", "claude-3-opus", raising=False)

    mock_message = MagicMock()
    mock_message.usage.input_tokens = 15
    mock_message.usage.output_tokens = 25
    mock_block = MagicMock()
    mock_block.text = ""
    mock_message.content = [mock_block]

    with patch("app.services.llm.json_completion.anthropic.AsyncAnthropic") as mock_anthropic_cls, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        mock_anthropic = MagicMock()
        mock_anthropic_cls.return_value = mock_anthropic
        mock_anthropic.messages.create = AsyncMock(return_value=mock_message)

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi")

        assert resp.provider == "anthropic"
        assert resp.content == "{}"  # fallback to empty dict
        mock_record.assert_called_once()


@pytest.mark.unit
async def test_complete_json_parses_response(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "mock", raising=False)

    gw = JsonCompletionGateway()
    result = await gw.complete_json(prompt="test")
    assert result == {}


@pytest.mark.unit
async def test_fallback_tries_google_then_groq_when_google_fails(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "unknown", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)
    monkeypatch.setattr(config.settings, "GROQ_API_KEY", "k", raising=False)

    mock_completion = MagicMock()
    mock_completion.usage.prompt_tokens = 10
    mock_completion.usage.completion_tokens = 20
    mock_completion.choices[0].message.content = '{"result": "ok"}'

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client, \
         patch("app.services.llm.json_completion.AsyncGroq") as mock_groq_cls, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        # Google fails
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Google error", request=MagicMock(), response=MagicMock())
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        # Groq succeeds
        mock_groq = MagicMock()
        mock_groq_cls.return_value = mock_groq
        mock_groq.chat.completions.create = AsyncMock(return_value=mock_completion)

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi")

        assert resp.provider == "groq"
        mock_record.assert_called_once()


@pytest.mark.unit
async def test_explicit_google_fails_to_fallback_groq(monkeypatch):
    from app.core import config
    # Set explicit provider to google but it fails, should not fallback
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Google error", request=MagicMock(), response=MagicMock())
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        gw = JsonCompletionGateway()
        with pytest.raises(httpx.HTTPStatusError):
            await gw.complete(prompt="hi")


@pytest.mark.unit
async def test_fallback_collects_errors_when_all_providers_fail(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "unknown", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)
    monkeypatch.setattr(config.settings, "GROQ_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_MODEL", "claude-3-opus", raising=False)

    with patch("app.services.llm.json_completion.httpx.AsyncClient") as mock_client, \
         patch("app.services.llm.json_completion.AsyncGroq") as mock_groq_cls, \
         patch("app.services.llm.json_completion.anthropic.AsyncAnthropic") as mock_anthropic_cls:
        # All fail
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock())
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        mock_groq = MagicMock()
        mock_groq_cls.return_value = mock_groq
        mock_groq.chat.completions.create = AsyncMock(side_effect=Exception("Groq error"))

        mock_anthropic = MagicMock()
        mock_anthropic_cls.return_value = mock_anthropic
        mock_anthropic.messages.create = AsyncMock(side_effect=Exception("Anthropic error"))

        gw = JsonCompletionGateway()
        with pytest.raises(JsonCompletionError, match="No JSON LLM provider succeeded"):
            await gw.complete(prompt="hi")
