"""Embedding providers for semantic retrieval.

Production uses Azure OpenAI's approved embedding deployment. CI uses a local,
deterministic hashing provider that performs no external inference and emits the
same 1536-dimensional shape as production.
"""
from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass
from typing import Protocol

from app.models.retrieval import EMBEDDING_DIMENSIONS

_TOKEN_RE = re.compile(r"[\w'-]+", re.UNICODE)


class EmbeddingProviderError(RuntimeError):
    """A bounded provider error safe for fallback decisions."""


class EmbeddingProvider(Protocol):
    name: str
    model: str
    version: str
    dimensions: int

    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...


@dataclass(frozen=True)
class EmbeddingProviderSettings:
    provider: str
    environment: str
    azure_endpoint: str
    azure_api_key: str
    azure_deployment: str
    azure_api_version: str
    dimensions: int = EMBEDDING_DIMENSIONS

    @classmethod
    def from_env(cls) -> "EmbeddingProviderSettings":
        environment = (os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "development").lower()
        configured_provider = os.getenv("SEMANTIC_EMBEDDING_PROVIDER", "").strip().lower()
        provider = configured_provider or (
            "deterministic" if environment in {"development", "test"} else "azure_openai"
        )
        return cls(
            provider=provider,
            environment=environment,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "").strip(),
            azure_api_key=os.getenv("AZURE_OPENAI_API_KEY", "").strip(),
            azure_deployment=(
                os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
                or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
                or "text-embedding-3-small"
            ).strip(),
            azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01").strip(),
        )


class DeterministicEmbeddingProvider:
    """Hashing-vector provider for tests and local evaluation only."""

    name = "deterministic_hashing"
    model = "eduboost-hashing-1536"
    version = "1.0"
    dimensions = EMBEDDING_DIMENSIONS

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    async def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text)

    @classmethod
    def _embed_one(cls, text: str) -> list[float]:
        tokens = [token.casefold() for token in _TOKEN_RE.findall(text) if token.strip()]
        if not tokens:
            raise EmbeddingProviderError("Cannot embed empty text.")
        vector = [0.0] * cls.dimensions
        features = list(tokens)
        features.extend(f"{a}::{b}" for a, b in zip(tokens, tokens[1:]))
        for feature in features:
            digest = hashlib.sha256(feature.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % cls.dimensions
            sign = -1.0 if digest[4] & 1 else 1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if not norm:
            raise EmbeddingProviderError("Embedding normalization failed.")
        return [value / norm for value in vector]


class AzureOpenAIEmbeddingProvider:
    name = "azure_openai"
    version = "2024-02-01"
    dimensions = EMBEDDING_DIMENSIONS

    def __init__(self, settings: EmbeddingProviderSettings) -> None:
        if not settings.azure_endpoint or not settings.azure_api_key:
            raise EmbeddingProviderError("Azure OpenAI embedding endpoint/key are not configured.")
        self.model = settings.azure_deployment
        self.version = settings.azure_api_version
        self._settings = settings

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts or any(not text.strip() for text in texts):
            raise EmbeddingProviderError("Embedding inputs must be non-empty strings.")
        try:
            from openai import AsyncAzureOpenAI

            client = AsyncAzureOpenAI(
                azure_endpoint=self._settings.azure_endpoint,
                api_key=self._settings.azure_api_key,
                api_version=self._settings.azure_api_version,
            )
            response = await client.embeddings.create(model=self.model, input=texts)
            vectors = [list(item.embedding) for item in sorted(response.data, key=lambda item: item.index)]
        except Exception as exc:  # provider SDK errors are normalized for fallback
            raise EmbeddingProviderError(f"Azure embedding request failed: {type(exc).__name__}") from exc
        if len(vectors) != len(texts):
            raise EmbeddingProviderError("Azure embedding response count does not match input count.")
        for vector in vectors:
            if len(vector) != self.dimensions:
                raise EmbeddingProviderError(
                    f"Azure embedding dimension mismatch: expected {self.dimensions}, received {len(vector)}."
                )
        return vectors

    async def embed_query(self, text: str) -> list[float]:
        return (await self.embed([text]))[0]


def build_embedding_provider(
    settings: EmbeddingProviderSettings | None = None,
) -> EmbeddingProvider:
    resolved = settings or EmbeddingProviderSettings.from_env()
    if resolved.dimensions != EMBEDDING_DIMENSIONS:
        raise EmbeddingProviderError(
            f"Phase 2 requires {EMBEDDING_DIMENSIONS}-dimensional embeddings."
        )
    if resolved.provider == "deterministic":
        if resolved.environment in {"staging", "production"}:
            raise EmbeddingProviderError(
                "The deterministic embedding provider is forbidden outside development/test."
            )
        return DeterministicEmbeddingProvider()
    if resolved.provider == "azure_openai":
        return AzureOpenAIEmbeddingProvider(resolved)
    raise EmbeddingProviderError(f"Unsupported semantic embedding provider: {resolved.provider}")
