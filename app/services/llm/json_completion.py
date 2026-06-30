"""Shared JSON completion gateway for generation pipelines."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import anthropic
import httpx
from groq import AsyncGroq

from app.core.config import settings
from app.core.metrics import record_llm_tokens


@dataclass(frozen=True)
class JsonCompletionResponse:
    content: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


class JsonCompletionError(RuntimeError):
    """Raised when no configured provider returns a usable JSON response."""


class JsonCompletionGateway:
    """Provider-neutral JSON completion gateway used by batch content factories."""

    async def complete(
        self,
        *,
        prompt: str,
        system: str = "Return valid JSON only. Do not include markdown.",
        max_tokens: int = 1024,
        temperature: float = 0.2,
        response_format: str = "json",
        operation: str = "content_generation",
    ) -> JsonCompletionResponse:
        provider = settings.LLM_PROVIDER
        if provider == "mock":
            return self._mock_response(prompt)
        if provider == "google":
            return await self._call_google(prompt, system=system, max_tokens=max_tokens, temperature=temperature, operation=operation)
        if provider == "groq":
            return await self._call_groq(prompt, system=system, max_tokens=max_tokens, temperature=temperature, operation=operation)
        if provider == "anthropic":
            return await self._call_anthropic(prompt, system=system, max_tokens=max_tokens, temperature=temperature, operation=operation)

        errors: list[str] = []
        if settings.GOOGLE_API_KEY:
            try:
                return await self._call_google(prompt, system=system, max_tokens=max_tokens, temperature=temperature, operation=operation)
            except Exception as exc:  # pragma: no cover - provider/network specific
                errors.append(f"google: {exc}")
        if settings.GROQ_API_KEY:
            try:
                return await self._call_groq(prompt, system=system, max_tokens=max_tokens, temperature=temperature, operation=operation)
            except Exception as exc:  # pragma: no cover - provider/network specific
                errors.append(f"groq: {exc}")
        if settings.ANTHROPIC_API_KEY:
            try:
                return await self._call_anthropic(prompt, system=system, max_tokens=max_tokens, temperature=temperature, operation=operation)
            except Exception as exc:  # pragma: no cover - provider/network specific
                errors.append(f"anthropic: {exc}")
        suffix = f": {'; '.join(errors)}" if errors else ""
        raise JsonCompletionError(f"No JSON LLM provider succeeded{suffix}")

    async def complete_json(self, **kwargs: Any) -> dict[str, Any]:
        response = await self.complete(**kwargs)
        return parse_json_response(response.content)

    def _mock_response(self, prompt: str) -> JsonCompletionResponse:
        if "correct_answer" in prompt or "answer key" in prompt.lower():
            content = json.dumps({"correct_answer": "A", "confidence": 0.8})
        else:
            content = "{}"
        return JsonCompletionResponse(content=content, provider="mock", model="mock-json")

    async def _call_google(
        self,
        prompt: str,
        *,
        system: str,
        max_tokens: int,
        temperature: float,
        operation: str,
    ) -> JsonCompletionResponse:
        if not settings.GOOGLE_API_KEY:
            raise JsonCompletionError("Google Gemini API key not configured")
        model = settings.GOOGLE_MODEL.removeprefix("models/")
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"Content-Type": "application/json", "x-goog-api-key": settings.GOOGLE_API_KEY},
                json={
                    "systemInstruction": {"parts": [{"text": system}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "maxOutputTokens": max_tokens,
                        "temperature": temperature,
                    },
                },
            )
        response.raise_for_status()
        payload = response.json()
        usage = payload.get("usageMetadata") or {}
        input_tokens = int(usage.get("promptTokenCount") or 0)
        output_tokens = int(usage.get("candidatesTokenCount") or 0)
        record_llm_tokens("google", model, operation, input_tokens, output_tokens)
        candidates = payload.get("candidates") or []
        if not candidates:
            raise JsonCompletionError("Google Gemini returned no candidates")
        parts = (candidates[0].get("content") or {}).get("parts") or []
        content = "".join(str(part.get("text") or "") for part in parts).strip()
        if not content:
            raise JsonCompletionError("Google Gemini returned an empty response")
        return JsonCompletionResponse(content=content, provider="google", model=model, prompt_tokens=input_tokens, completion_tokens=output_tokens)

    async def _call_groq(
        self,
        prompt: str,
        *,
        system: str,
        max_tokens: int,
        temperature: float,
        operation: str,
    ) -> JsonCompletionResponse:
        if not settings.GROQ_API_KEY:
            raise JsonCompletionError("Groq API key not configured")
        model = getattr(settings, "GROQ_MODEL", "llama3-70b-8192")
        completion = await AsyncGroq(api_key=settings.GROQ_API_KEY).chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            temperature=temperature,
        )
        usage = completion.usage
        input_tokens = int(usage.prompt_tokens if usage else 0)
        output_tokens = int(usage.completion_tokens if usage else 0)
        record_llm_tokens("groq", model, operation, input_tokens, output_tokens)
        return JsonCompletionResponse(
            content=completion.choices[0].message.content or "{}",
            provider="groq",
            model=model,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
        )

    async def _call_anthropic(
        self,
        prompt: str,
        *,
        system: str,
        max_tokens: int,
        temperature: float,
        operation: str,
    ) -> JsonCompletionResponse:
        if not settings.ANTHROPIC_API_KEY:
            raise JsonCompletionError("Anthropic API key not configured")
        model = settings.ANTHROPIC_MODEL
        message = await anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY).messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        record_llm_tokens("anthropic", model, operation, message.usage.input_tokens, message.usage.output_tokens)
        content = "".join(getattr(block, "text", "") for block in message.content).strip()
        return JsonCompletionResponse(
            content=content or "{}",
            provider="anthropic",
            model=model,
            prompt_tokens=message.usage.input_tokens,
            completion_tokens=message.usage.output_tokens,
        )


def parse_json_response(raw: str) -> dict[str, Any]:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise JsonCompletionError(f"LLM response is not valid JSON: {exc}") from exc
