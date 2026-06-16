from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from app.models.retrieval import EMBEDDING_DIMENSIONS
from app.services.semantic_retrieval.embedding import EmbeddingProviderError
from app.services.semantic_retrieval.service import FallbackPolicy, SemanticRetrievalService
from app.services.semantic_retrieval.types import RetrievalFilters, RetrievalHit


class FakeProvider:
    name = "fake"
    model = "fake-model"
    version = "1"
    dimensions = EMBEDDING_DIMENSIONS

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    async def embed_query(self, text: str) -> list[float]:
        if self.fail:
            raise EmbeddingProviderError("offline")
        return [0.0] * EMBEDDING_DIMENSIONS

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * EMBEDDING_DIMENSIONS for _ in texts]


@dataclass
class FakeRepository:
    semantic_hits: list[RetrievalHit] = field(default_factory=list)
    fulltext_hits: list[RetrievalHit] = field(default_factory=list)
    semantic_error: Exception | None = None
    calls: list[tuple[str, RetrievalFilters]] = field(default_factory=list)

    async def semantic_search(self, session, *, query_vector, filters, limit):
        self.calls.append(("semantic", filters))
        if self.semantic_error:
            raise self.semantic_error
        return self.semantic_hits[:limit]

    async def full_text_search(self, session, *, query, filters, limit):
        self.calls.append(("full_text", filters))
        return self.fulltext_hits[:limit]

    async def fetch_approved_chunks(self, session, *, chunk_ids, filters):
        self.calls.append(("fetch", filters))
        return [hit for hit in self.semantic_hits if hit.chunk_id in chunk_ids]


def hit(chunk_id: str, mode: str = "semantic") -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        document_id="doc-1",
        document_version_id="v1",
        title="CAPS",
        content="Whole numbers and place value",
        heading="Whole numbers",
        section_path="1",
        page_start=1,
        page_end=1,
        scope_id="g4-math",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        permission_scope="public",
        document_status="approved",
        chunk_status="approved",
        license_status="government_open",
        quality_score=0.9,
        source_hash="sha256:doc",
        chunk_hash="sha256:chunk",
        curriculum_mapping_id="map-1",
        score=0.9,
        retrieval_mode=mode,  # type: ignore[arg-type]
    )


FILTERS = RetrievalFilters(
    scope_id="g4-math",
    caps_ref="4.M.1.1",
    grade=4,
    subject_code="MATH",
    language="en",
)


@pytest.mark.asyncio
async def test_semantic_hits_return_without_fallback() -> None:
    repository = FakeRepository(semantic_hits=[hit("chunk-1")])
    service = SemanticRetrievalService(
        embedding_provider=FakeProvider(), repository=repository  # type: ignore[arg-type]
    )
    result = await service.search(object(), query="whole numbers", filters=FILTERS)
    assert result.mode == "semantic"
    assert result.fallback_reason is None
    assert [call[0] for call in repository.calls] == ["semantic"]


@pytest.mark.asyncio
async def test_embedding_failure_uses_fulltext_with_identical_filters() -> None:
    repository = FakeRepository(fulltext_hits=[hit("chunk-1", "full_text")])
    service = SemanticRetrievalService(
        embedding_provider=FakeProvider(fail=True), repository=repository  # type: ignore[arg-type]
    )
    result = await service.search(object(), query="whole numbers", filters=FILTERS)
    assert result.mode == "full_text"
    assert result.fallback_reason == "embedding_unavailable:EmbeddingProviderError"
    assert repository.calls == [("full_text", FILTERS)]


@pytest.mark.asyncio
async def test_vector_query_transient_failure_uses_fulltext_only_when_policy_allows() -> None:
    repository = FakeRepository(
        semantic_error=ConnectionError("vector unavailable"),
        fulltext_hits=[hit("chunk-1", "full_text")],
    )
    service = SemanticRetrievalService(
        embedding_provider=FakeProvider(), repository=repository  # type: ignore[arg-type]
    )
    result = await service.search(object(), query="whole numbers", filters=FILTERS)
    assert result.mode == "full_text"
    assert result.fallback_reason == "vector_temporarily_unavailable:ConnectionError"
    assert [call[0] for call in repository.calls] == ["semantic", "full_text"]

    strict_repository = FakeRepository(
        semantic_error=ConnectionError("vector unavailable"),
        fulltext_hits=[hit("chunk-1", "full_text")],
    )
    strict = SemanticRetrievalService(
        embedding_provider=FakeProvider(),
        repository=strict_repository,  # type: ignore[arg-type]
        fallback_policy=FallbackPolicy(on_vector_error=False),
    )
    with pytest.raises(ConnectionError, match="vector unavailable"):
        await strict.search(object(), query="whole numbers", filters=FILTERS)
    assert [call[0] for call in strict_repository.calls] == ["semantic"]


@pytest.mark.asyncio
async def test_vector_query_generic_runtime_error_fails_closed() -> None:
    repository = FakeRepository(
        semantic_error=RuntimeError("vector schema or query defect"),
        fulltext_hits=[hit("chunk-1", "full_text")],
    )
    service = SemanticRetrievalService(
        embedding_provider=FakeProvider(), repository=repository  # type: ignore[arg-type]
    )

    with pytest.raises(RuntimeError, match="schema or query defect"):
        await service.search(object(), query="whole numbers", filters=FILTERS)

    # A programming/schema/integrity-style failure must never be hidden by
    # a full-text fallback.
    assert [call[0] for call in repository.calls] == ["semantic"]


@pytest.mark.asyncio
async def test_requested_chunk_lookup_fails_closed_for_missing_or_filtered_chunks() -> None:
    repository = FakeRepository(semantic_hits=[hit("chunk-1")])
    service = SemanticRetrievalService(
        embedding_provider=FakeProvider(), repository=repository  # type: ignore[arg-type]
    )
    with pytest.raises(LookupError, match="missing or fail"):
        await service.fetch_approved_chunks(
            object(), chunk_ids=["chunk-1", "chunk-2"], filters=FILTERS
        )
