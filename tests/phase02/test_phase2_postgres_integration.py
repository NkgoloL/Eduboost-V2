from __future__ import annotations

import os

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.semantic_retrieval.embedding import (
    DeterministicEmbeddingProvider,
    EmbeddingProviderError,
)
from app.services.semantic_retrieval.indexing import (
    RetrievalIndexingService,
    SourceChunkInput,
    SourceDocumentInput,
)
from app.services.semantic_retrieval.repository import SemanticRetrievalRepository
from app.services.semantic_retrieval.service import SemanticRetrievalService
from app.services.semantic_retrieval.types import RetrievalFilters

DATABASE_URL = os.getenv("PHASE2_TEST_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="PHASE2_TEST_DATABASE_URL must point to a disposable pgvector PostgreSQL database.",
)


class FailingEmbeddingProvider:
    name = "failing"
    model = "failing"
    version = "1"
    dimensions = 1536

    async def embed_query(self, text: str) -> list[float]:
        raise EmbeddingProviderError("forced test outage")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingProviderError("forced test outage")


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await session.execute(text("TRUNCATE retrieval_source_chunks, retrieval_source_documents CASCADE"))
        await session.commit()
        yield session
        await session.rollback()
    await engine.dispose()


async def seed_corpus(session) -> None:
    provider = DeterministicEmbeddingProvider()
    indexing = RetrievalIndexingService(embedding_provider=provider)
    await indexing.upsert_document(
        session,
        document=SourceDocumentInput(
            document_id="caps-g4-math-v1",
            document_version_id="2026.1",
            title="CAPS Grade 4 Mathematics",
            scope_id="g4-math",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
            status="approved",
            permission_scope="public",
            license_status="government_open",
            quality_score=0.95,
        ),
        chunks=[
            SourceChunkInput(
                chunk_id="whole-numbers",
                chunk_index=0,
                heading="Whole numbers and place value",
                content="Learners count, order, compare and represent whole numbers using place value.",
                curriculum_mapping_id="map-whole",
            ),
            SourceChunkInput(
                chunk_id="geometry",
                chunk_index=1,
                heading="Geometry",
                content="Learners identify triangles, quadrilaterals, angles and symmetry.",
                curriculum_mapping_id="map-geometry",
            ),
        ],
    )
    await indexing.upsert_document(
        session,
        document=SourceDocumentInput(
            document_id="draft-g4-math",
            document_version_id="draft-1",
            title="Unapproved draft",
            scope_id="g4-math",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
            status="draft",
            permission_scope="public",
            license_status="internal_review",
            quality_score=1.0,
        ),
        chunks=[
            SourceChunkInput(
                chunk_id="draft-whole-numbers",
                chunk_index=0,
                heading="Whole numbers",
                content="Whole numbers whole numbers whole numbers place value.",
            )
        ],
    )
    await indexing.upsert_document(
        session,
        document=SourceDocumentInput(
            document_id="caps-g5-math-v1",
            document_version_id="2026.1",
            title="CAPS Grade 5 Mathematics",
            scope_id="g5-math",
            caps_ref="5.M.1.1",
            grade=5,
            subject_code="MATH",
            language="en",
            status="approved",
            permission_scope="public",
            license_status="government_open",
            quality_score=0.95,
        ),
        chunks=[
            SourceChunkInput(
                chunk_id="g5-whole-numbers",
                chunk_index=0,
                heading="Whole numbers Grade 5",
                content="Grade five learners extend whole number place value.",
            )
        ],
    )
    await session.commit()


@pytest.mark.asyncio
async def test_pgvector_schema_indexes_and_dimension(session) -> None:
    extension = await session.scalar(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
    assert extension == "vector"
    formatted = await session.scalar(
        text(
            """
            SELECT format_type(a.atttypid, a.atttypmod)
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            WHERE c.relname = 'retrieval_source_chunks'
              AND a.attname = 'embedding'
              AND NOT a.attisdropped
            """
        )
    )
    assert formatted == "vector(1536)"
    indexes = {
        row[0]
        for row in (
            await session.execute(
                text(
                    """
                    SELECT indexname
                    FROM pg_indexes
                    WHERE tablename = 'retrieval_source_chunks'
                    """
                )
            )
        ).all()
    }
    assert "ix_retrieval_chunks_embedding_hnsw" in indexes
    assert "ix_retrieval_chunks_fulltext_gin" in indexes


@pytest.mark.asyncio
async def test_semantic_search_applies_approval_and_scope_filters(session) -> None:
    await seed_corpus(session)
    service = SemanticRetrievalService(
        embedding_provider=DeterministicEmbeddingProvider()
    )
    result = await service.search(
        session,
        query="whole numbers place value",
        filters=RetrievalFilters(
            scope_id="g4-math",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
            min_quality_score=0.5,
        ),
        limit=5,
    )
    returned = [hit.chunk_id for hit in result.hits]
    assert returned[0] == "whole-numbers"
    assert "draft-whole-numbers" not in returned
    assert "g5-whole-numbers" not in returned
    assert all(hit.scope_id == "g4-math" for hit in result.hits)


@pytest.mark.asyncio
async def test_fulltext_fallback_preserves_the_same_approval_filters(session) -> None:
    await seed_corpus(session)
    service = SemanticRetrievalService(embedding_provider=FailingEmbeddingProvider())
    result = await service.search(
        session,
        query="whole numbers place value",
        filters=RetrievalFilters(
            scope_id="g4-math",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
        ),
        limit=5,
    )
    assert result.mode == "full_text"
    assert result.fallback_reason == "embedding_unavailable:EmbeddingProviderError"
    returned = [hit.chunk_id for hit in result.hits]
    assert "whole-numbers" in returned
    assert "draft-whole-numbers" not in returned
    assert "g5-whole-numbers" not in returned


@pytest.mark.asyncio
async def test_requested_chunk_fetch_fails_closed_for_unapproved_chunk(session) -> None:
    await seed_corpus(session)
    service = SemanticRetrievalService(
        embedding_provider=DeterministicEmbeddingProvider()
    )
    filters = RetrievalFilters(scope_id="g4-math", caps_ref="4.M.1.1")
    with pytest.raises(LookupError, match="missing or fail"):
        await service.fetch_approved_chunks(
            session,
            chunk_ids=["draft-whole-numbers"],
            filters=filters,
        )


@pytest.mark.asyncio
async def test_document_reindex_removes_stale_chunks(session) -> None:
    provider = DeterministicEmbeddingProvider()
    indexing = RetrievalIndexingService(embedding_provider=provider)
    document = SourceDocumentInput(
        document_id="versioned-doc",
        document_version_id="v1",
        title="Versioned source",
        scope_id="g4-math",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        status="approved",
        permission_scope="public",
        license_status="government_open",
        quality_score=0.9,
    )
    await indexing.upsert_document(
        session,
        document=document,
        chunks=[
            SourceChunkInput(chunk_id="keep", chunk_index=0, content="whole numbers"),
            SourceChunkInput(chunk_id="remove", chunk_index=1, content="old material"),
        ],
    )
    await indexing.upsert_document(
        session,
        document=SourceDocumentInput(**{**document.__dict__, "document_version_id": "v2"}),
        chunks=[SourceChunkInput(chunk_id="keep", chunk_index=0, content="whole numbers updated")],
    )
    await session.commit()
    ids = {
        row[0]
        for row in (
            await session.execute(
                text("SELECT chunk_id FROM retrieval_source_chunks WHERE document_id='versioned-doc'")
            )
        ).all()
    }
    assert ids == {"keep"}


@pytest.mark.asyncio
async def test_incompatible_license_is_excluded_even_if_status_is_approved(session) -> None:
    provider = DeterministicEmbeddingProvider()
    indexing = RetrievalIndexingService(embedding_provider=provider)
    await indexing.upsert_document(
        session,
        document=SourceDocumentInput(
            document_id="bad-license",
            document_version_id="v1",
            title="Restricted source",
            scope_id="g4-math",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
            status="approved",
            permission_scope="public",
            license_status="all_rights_reserved",
            quality_score=1.0,
        ),
        chunks=[
            SourceChunkInput(
                chunk_id="bad-license-chunk",
                chunk_index=0,
                content="whole numbers place value whole numbers",
            )
        ],
    )
    await session.commit()
    result = await SemanticRetrievalService(
        embedding_provider=provider
    ).search(
        session,
        query="whole numbers place value",
        filters=RetrievalFilters(scope_id="g4-math", caps_ref="4.M.1.1"),
        limit=5,
    )
    assert "bad-license-chunk" not in {hit.chunk_id for hit in result.hits}


@pytest.mark.asyncio
async def test_hnsw_query_plan_is_available(session) -> None:
    await seed_corpus(session)
    provider = DeterministicEmbeddingProvider()
    vector = await provider.embed_query("whole numbers place value")
    await session.execute(text("SET LOCAL enable_seqscan = off"))
    plan = await SemanticRetrievalRepository().explain_hnsw_probe(
        session,
        query_vector=vector,
    )
    assert any("ix_retrieval_chunks_embedding_hnsw" in line for line in plan), plan
