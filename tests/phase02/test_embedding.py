from __future__ import annotations

import math

import pytest

from app.models.retrieval import EMBEDDING_DIMENSIONS, vector_literal
from app.services.semantic_retrieval.embedding import (
    DeterministicEmbeddingProvider,
    EmbeddingProviderError,
    EmbeddingProviderSettings,
    build_embedding_provider,
)


@pytest.mark.asyncio
async def test_deterministic_embedding_has_production_shape_and_unit_norm() -> None:
    provider = DeterministicEmbeddingProvider()
    vector = await provider.embed_query("whole numbers place value grade four")
    assert len(vector) == EMBEDDING_DIMENSIONS
    assert math.isclose(sum(value * value for value in vector), 1.0, rel_tol=1e-6)


@pytest.mark.asyncio
async def test_deterministic_embedding_is_semantically_token_sensitive() -> None:
    provider = DeterministicEmbeddingProvider()
    query = await provider.embed_query("place value whole numbers")
    related = await provider.embed_query("whole numbers and place value")
    unrelated = await provider.embed_query("triangles angles geometry")
    related_score = sum(a * b for a, b in zip(query, related))
    unrelated_score = sum(a * b for a, b in zip(query, unrelated))
    assert related_score > unrelated_score


def test_deterministic_provider_forbidden_in_production() -> None:
    settings = EmbeddingProviderSettings(
        provider="deterministic",
        environment="production",
        azure_endpoint="",
        azure_api_key="",
        azure_deployment="text-embedding-3-small",
        azure_api_version="2024-02-01",
    )
    with pytest.raises(EmbeddingProviderError, match="forbidden"):
        build_embedding_provider(settings)


def test_vector_literal_validates_dimension_and_finite_values() -> None:
    literal = vector_literal([0.0] * EMBEDDING_DIMENSIONS)
    assert literal.startswith("[") and literal.endswith("]")
    with pytest.raises(ValueError, match="1536"):
        vector_literal([0.0])
    with pytest.raises(ValueError, match="finite"):
        vector_literal([float("nan")] * EMBEDDING_DIMENSIONS)

def test_default_development_provider_is_deterministic(monkeypatch) -> None:
    monkeypatch.delenv("SEMANTIC_EMBEDDING_PROVIDER", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    assert isinstance(build_embedding_provider(), DeterministicEmbeddingProvider)
