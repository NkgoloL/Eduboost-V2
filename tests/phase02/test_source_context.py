from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.services.content_generation.source_context import ContentGenerationSourceContextService
from app.services.semantic_retrieval.types import RetrievalHit, RetrievalResult


def hit(chunk_id: str = "chunk-1") -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        document_id="caps-doc",
        document_version_id="2026.1",
        title="CAPS Grade 4 Mathematics",
        content="Learners count, order and compare whole numbers.",
        heading="Whole numbers",
        section_path="Numbers/Whole numbers",
        page_start=12,
        page_end=13,
        scope_id="g4-math",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        permission_scope="public",
        document_status="approved",
        chunk_status="approved",
        license_status="government_open",
        quality_score=0.95,
        source_hash="sha256:source",
        chunk_hash="sha256:chunk",
        curriculum_mapping_id="map-1",
        score=0.98,
        retrieval_mode="semantic",
    )


@dataclass
class FakeRetrieval:
    fail_missing: bool = False

    async def search(self, session, *, query, filters, limit):
        return RetrievalResult(
            query_fingerprint="fp",
            mode="semantic",
            hits=[hit()],
            fallback_reason=None,
            embedding_model="model",
            embedding_version="1",
            elapsed_ms=1,
        )

    async def fetch_approved_chunks(self, session, *, chunk_ids, filters):
        if self.fail_missing:
            raise LookupError("Requested chunks are missing or fail approval filters")
        return [hit(chunk_ids[0])]


@pytest.mark.asyncio
async def test_generation_context_uses_retrieval_provenance() -> None:
    service = ContentGenerationSourceContextService(retrieval_service=FakeRetrieval())  # type: ignore[arg-type]
    result = await service.build_context(
        object(),
        scope_id="g4-math",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
    )
    assert result.passed
    assert result.chunks[0].source_document_id == "caps-doc"
    assert result.chunks[0].source_chunk_id == "chunk-1"
    assert result.chunks[0].source_hash == "sha256:source"


@pytest.mark.asyncio
async def test_generation_context_fails_closed_when_requested_chunk_is_unavailable() -> None:
    service = ContentGenerationSourceContextService(
        retrieval_service=FakeRetrieval(fail_missing=True)  # type: ignore[arg-type]
    )
    result = await service.build_context(
        object(),
        scope_id="g4-math",
        caps_ref="4.M.1.1",
        requested_chunk_ids=["blocked-chunk"],
    )
    assert not result.passed
    assert "missing" in result.errors[0]
