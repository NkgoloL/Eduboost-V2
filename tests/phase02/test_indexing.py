from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from app.models.retrieval import EMBEDDING_DIMENSIONS
from app.services.semantic_retrieval.indexing import (
    RetrievalIndexingService,
    SourceChunkInput,
    SourceDocumentInput,
)


@dataclass
class RecordingProvider:
    name: str = "recording"
    model: str = "recording-model"
    version: str = "1"
    dimensions: int = EMBEDDING_DIMENSIONS
    batches: list[list[str]] = field(default_factory=list)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.batches.append(list(texts))
        return [[0.0] * self.dimensions for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [0.0] * self.dimensions


class RecordingSession:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    async def execute(self, statement, params=None):
        self.calls.append((str(statement), params))
        return None


def document(**overrides: Any) -> SourceDocumentInput:
    values: dict[str, Any] = {
        "document_id": "doc-1",
        "document_version_id": "v1",
        "title": "CAPS Grade 4 Mathematics",
        "scope_id": "g4-math",
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "status": "approved",
        "permission_scope": "public",
        "license_status": "government_open",
        "quality_score": 0.9,
    }
    values.update(overrides)
    return SourceDocumentInput(**values)


@pytest.mark.asyncio
async def test_only_searchable_chunks_receive_embeddings() -> None:
    provider = RecordingProvider()
    session = RecordingSession()
    service = RetrievalIndexingService(embedding_provider=provider)

    await service.upsert_document(
        session,  # type: ignore[arg-type]
        document=document(),
        chunks=[
            SourceChunkInput(chunk_id="approved", chunk_index=0, content="whole numbers"),
            SourceChunkInput(
                chunk_id="draft",
                chunk_index=1,
                content="unreviewed material",
                status="draft",
            ),
        ],
    )

    assert provider.batches == [["whole numbers"]]
    chunk_params = [
        params
        for sql, params in session.calls
        if "INSERT INTO retrieval_source_chunks" in sql
    ]
    assert chunk_params[0]["embedding"] is not None
    assert chunk_params[1]["embedding"] is None
    assert chunk_params[1]["dimension"] is None


@pytest.mark.asyncio
async def test_incompatible_license_is_never_embedded() -> None:
    provider = RecordingProvider()
    session = RecordingSession()
    service = RetrievalIndexingService(embedding_provider=provider)

    await service.upsert_document(
        session,  # type: ignore[arg-type]
        document=document(license_status="all_rights_reserved"),
        chunks=[SourceChunkInput(chunk_id="restricted", chunk_index=0, content="whole numbers")],
    )

    assert provider.batches == []
    chunk_params = [
        params
        for sql, params in session.calls
        if "INSERT INTO retrieval_source_chunks" in sql
    ]
    assert chunk_params[0]["embedding"] is None
