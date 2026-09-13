import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.content_generation.source_context import (
    ContentGenerationSourceContextService,
)
from app.services.semantic_retrieval.generation_context import (
    SemanticContentGenerationSourceContextService,
    SemanticSourceContextResult,
)

from app.services.semantic_retrieval.types import (
    EvaluationCase,
    EvaluationMetrics,
    RetrievalFilters,
    RetrievalHit,
    RetrievalResult,
)


from typing import Any, cast


def _make_hit(**kwargs: Any) -> RetrievalHit:
    hit_data: dict[str, Any] = {
        "chunk_id": "chk_01",
        "document_id": "doc_01",
        "document_version_id": "v1",
        "title": "Fraction Lesson Title",
        "content": "A fraction is part of a whole.",
        "heading": "Introduction",
        "section_path": "Chapter 1",
        "page_start": 1,
        "page_end": 2,
        "scope_id": "scope_math_g4",
        "caps_ref": "4.MATH.1",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "permission_scope": "public",
        "document_status": "approved",
        "chunk_status": "indexed",
        "license_status": "open",
        "quality_score": 0.95,
        "source_hash": "sha_src",
        "chunk_hash": "sha_chk",
        "curriculum_mapping_id": "map_01",
        "score": 0.88,
        "retrieval_mode": "semantic",
    }
    hit_data.update(kwargs)
    return RetrievalHit(**cast(Any, hit_data))


def test_semantic_retrieval_types():
    filters = RetrievalFilters(
        scope_id=" scope_01 ",
        caps_ref=" CAPS.01 ",
        grade=4,
        subject_code=" MATH ",
        language=" en ",
        permission_scope=" public ",
    )
    assert filters.scope_id == "scope_01"
    assert filters.caps_ref == "CAPS.01"
    assert filters.subject_code == "MATH"

    hit = _make_hit()
    prov = hit.provenance()
    assert prov["source_document_id"] == "doc_01"
    assert prov["source_title"] == "Fraction Lesson Title"
    assert prov["retrieval_score"] == 0.88

    res = RetrievalResult(
        query_fingerprint="fp1",
        mode="semantic",
        hits=[hit],
        fallback_reason=None,
        embedding_model="text-embedding-3-small",
        embedding_version="1",
        elapsed_ms=12.5,
    )
    assert len(res.hits) == 1

    case = EvaluationCase(
        case_id="c1",
        query="What is a fraction?",
        expected_chunk_ids=frozenset(["chk_01"]),
        filters=filters,
    )
    assert case.k == 5

    metrics = EvaluationMetrics(
        case_count=1,
        recall_at_k=1.0,
        mean_reciprocal_rank=1.0,
        precision_at_k=1.0,
        unsafe_hit_count=0,
        passed=True,
        thresholds={"recall": 0.8},
        case_results=[{"case_id": "c1", "passed": True}],
    )
    assert metrics.passed is True


@pytest.mark.asyncio
async def test_semantic_generation_context_service_success():
    retrieval_mock = MagicMock()
    hit = _make_hit()
    retrieval_mock.search = AsyncMock(
        return_value=RetrievalResult(
            query_fingerprint="fp",
            mode="semantic",
            hits=[hit],
            fallback_reason=None,
            embedding_model=None,
            embedding_version=None,
            elapsed_ms=1.0,
        )
    )
    retrieval_mock.fetch_approved_chunks = AsyncMock(return_value=[hit])

    service = SemanticContentGenerationSourceContextService(retrieval_service=retrieval_mock)
    session = AsyncMock()

    # 1. Search branch
    res_search = await service.build_context(
        session,
        scope_id="sc1",
        caps_ref="4.MATH.1",
    )
    assert res_search.passed is True
    assert len(res_search.chunks) == 1
    assert res_search.chunks[0].source_document_id == "doc_01"

    # 2. Fetch specific chunks branch
    res_chunks = await service.build_context(
        session,
        scope_id="sc1",
        caps_ref="4.MATH.1",
        requested_chunk_ids=["chk_01"],
    )
    assert res_chunks.passed is True
    assert len(res_chunks.chunks) == 1


@pytest.mark.asyncio
async def test_semantic_generation_context_service_errors():
    retrieval_mock = MagicMock()
    retrieval_mock.search = AsyncMock(return_value=RetrievalResult("fp", "semantic", [], None, None, None, 1.0))

    service = SemanticContentGenerationSourceContextService(retrieval_service=retrieval_mock)
    session = AsyncMock()

    # Empty chunks result
    res_empty = await service.build_context(session, scope_id="sc1", caps_ref="4.MATH.1")
    assert res_empty.passed is False
    assert any("No approved" in e for e in res_empty.errors)

    # ValueError / LookupError
    retrieval_mock.search = AsyncMock(side_effect=LookupError("Missing corpus"))
    res_lookup = await service.build_context(session, scope_id="sc1", caps_ref="4.MATH.1")
    assert res_lookup.passed is False
    assert "Missing corpus" in res_lookup.errors[0]

    # Generic Exception
    retrieval_mock.search = AsyncMock(side_effect=RuntimeError("Database crashed"))
    res_err = await service.build_context(session, scope_id="sc1", caps_ref="4.MATH.1")
    assert res_err.passed is False
    assert "Semantic retrieval failed: RuntimeError" in res_err.errors[0]


@pytest.mark.asyncio
async def test_semantic_repository_methods():
    from app.services.semantic_retrieval.repository import SemanticRetrievalRepository
    from app.services.semantic_retrieval.types import RetrievalFilters

    repo = SemanticRetrievalRepository()
    session = AsyncMock()

    row_data = {
        "chunk_id": "c1",
        "document_id": "d1",
        "document_version_id": "v1",
        "title": "Title 1",
        "content": "Sample content",
        "heading": "Heading 1",
        "section_path": "Sec 1",
        "page_start": 1,
        "page_end": 2,
        "scope_id": "sc1",
        "caps_ref": "4.M.1",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "permission_scope": "public",
        "document_status": "approved",
        "chunk_status": "indexed",
        "license_status": "open",
        "quality_score": 0.9,
        "source_hash": "sh1",
        "chunk_hash": "ch1",
        "curriculum_mapping_id": "map1",
        "score": 0.85,
        "embedding_model": "text-emb-3",
        "embedding_version": "1",
        "source_metadata": {"key": "val"},
    }
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [row_data]
    mock_result.all.return_value = [("Seq Scan on table",)]
    session.execute.return_value = mock_result

    filters = RetrievalFilters(scope_id="sc1", grade=4, subject_code="MATH")

    # 1. semantic_search
    hits = await repo.semantic_search(session, query_vector=[0.1] * 1536, filters=filters, limit=5)
    assert len(hits) == 1
    assert hits[0].chunk_id == "c1"
    assert hits[0].retrieval_mode == "semantic"

    # 2. full_text_search
    ft_hits = await repo.full_text_search(session, query="fractions", filters=filters, limit=5)
    assert len(ft_hits) == 1
    assert ft_hits[0].chunk_id == "c1"
    assert ft_hits[0].retrieval_mode == "full_text"

    # 3. fetch_approved_chunks
    empty_hits = await repo.fetch_approved_chunks(session, chunk_ids=[], filters=filters)
    assert empty_hits == []

    fetch_hits = await repo.fetch_approved_chunks(session, chunk_ids=["c1"], filters=filters)
    assert len(fetch_hits) == 1
    assert fetch_hits[0].chunk_id == "c1"

    # 4. explain_semantic_search & explain_hnsw_probe
    explain1 = await repo.explain_semantic_search(session, query_vector=[0.1] * 1536, filters=filters)
    assert len(explain1) == 1
    assert "Seq Scan" in explain1[0]

    explain2 = await repo.explain_hnsw_probe(session, query_vector=[0.1] * 1536)
    assert len(explain2) == 1


@pytest.mark.asyncio
async def test_embedding_providers_and_builder(monkeypatch):
    import sys
    from app.services.semantic_retrieval.embedding import (
        DeterministicEmbeddingProvider,
        AzureOpenAIEmbeddingProvider,
        build_embedding_provider,
        EmbeddingProviderError,
        EmbeddingProviderSettings,
    )

    # 1. DeterministicEmbeddingProvider
    det = DeterministicEmbeddingProvider()
    vecs = await det.embed(["first text", "second text"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 1536

    with pytest.raises(EmbeddingProviderError, match="Cannot embed empty text"):
        await det.embed_query("   ")

    # 2. AzureOpenAIEmbeddingProvider initialization error
    bad_settings = EmbeddingProviderSettings(
        provider="azure_openai",
        environment="test",
        azure_endpoint="",
        azure_api_key="",
        azure_deployment="dep",
        azure_api_version="2024-02-01",
    )
    with pytest.raises(EmbeddingProviderError, match="Azure OpenAI embedding endpoint/key"):
        AzureOpenAIEmbeddingProvider(bad_settings)

    # 3. AzureOpenAIEmbeddingProvider operations
    good_settings = EmbeddingProviderSettings(
        provider="azure_openai",
        environment="test",
        azure_endpoint="https://example.openai.azure.com",
        azure_api_key="secret",
        azure_deployment="text-emb",
        azure_api_version="2024-02-01",
    )
    provider = AzureOpenAIEmbeddingProvider(good_settings)

    with pytest.raises(EmbeddingProviderError, match="must be non-empty strings"):
        await provider.embed([])

    with pytest.raises(EmbeddingProviderError, match="must be non-empty strings"):
        await provider.embed(["   "])

    # Mock OpenAI client
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_item = MagicMock()
    mock_item.index = 0
    mock_item.embedding = [0.05] * 1536
    mock_resp.data = [mock_item]
    mock_client.embeddings.create = AsyncMock(return_value=mock_resp)

    mock_openai_module = MagicMock()
    mock_openai_module.AsyncAzureOpenAI.return_value = mock_client
    monkeypatch.setitem(sys.modules, "openai", mock_openai_module)

    res_vecs = await provider.embed(["valid text"])
    assert len(res_vecs) == 1
    assert len(res_vecs[0]) == 1536

    q_vec = await provider.embed_query("query text")
    assert len(q_vec) == 1536

    # Error handling in client call
    mock_client.embeddings.create = AsyncMock(side_effect=RuntimeError("connection dropped"))
    with pytest.raises(EmbeddingProviderError, match="Azure embedding request failed"):
        await provider.embed(["valid text"])

    # Count mismatch
    mock_resp.data = []
    mock_client.embeddings.create = AsyncMock(return_value=mock_resp)
    with pytest.raises(EmbeddingProviderError, match="count does not match"):
        await provider.embed(["valid text"])

    # Dimension mismatch
    mock_bad_dim = MagicMock()
    mock_bad_dim.index = 0
    mock_bad_dim.embedding = [0.1] * 512
    mock_resp.data = [mock_bad_dim]
    mock_client.embeddings.create = AsyncMock(return_value=mock_resp)
    with pytest.raises(EmbeddingProviderError, match="dimension mismatch"):
        await provider.embed(["valid text"])

    # 4. build_embedding_provider
    dim_settings = EmbeddingProviderSettings(
        provider="deterministic",
        environment="test",
        azure_endpoint="",
        azure_api_key="",
        azure_deployment="",
        azure_api_version="",
        dimensions=512,
    )
    with pytest.raises(EmbeddingProviderError, match="Phase 2 requires 1536-dimensional"):
        build_embedding_provider(dim_settings)

    prod_settings = EmbeddingProviderSettings(
        provider="deterministic",
        environment="production",
        azure_endpoint="",
        azure_api_key="",
        azure_deployment="",
        azure_api_version="",
    )
    with pytest.raises(EmbeddingProviderError, match="forbidden outside development/test"):
        build_embedding_provider(prod_settings)

    azure_prov = build_embedding_provider(good_settings)
    assert isinstance(azure_prov, AzureOpenAIEmbeddingProvider)

    unknown_settings = EmbeddingProviderSettings(
        provider="unknown_provider",
        environment="test",
        azure_endpoint="",
        azure_api_key="",
        azure_deployment="",
        azure_api_version="",
    )
    with pytest.raises(EmbeddingProviderError, match="Unsupported semantic embedding provider"):
        build_embedding_provider(unknown_settings)


@pytest.mark.asyncio
async def test_semantic_retrieval_service_branches():
    from app.services.semantic_retrieval.service import SemanticRetrievalService, FallbackPolicy
    from app.services.semantic_retrieval.types import RetrievalFilters
    from app.services.semantic_retrieval.embedding import EmbeddingProviderError
    from sqlalchemy.exc import OperationalError

    mock_repo = MagicMock()
    mock_embedding = MagicMock()
    mock_embedding.model = "test-model"
    mock_embedding.version = "1.0"
    mock_embedding.embed_query = AsyncMock(return_value=[0.1] * 1536)

    service = SemanticRetrievalService(
        repository=mock_repo,
        embedding_provider=mock_embedding,
        fallback_policy=FallbackPolicy(
            on_embedding_error=False,
            on_vector_error=False,
            on_no_vector_hits=False,
        ),
    )
    session = AsyncMock()
    filters = RetrievalFilters(scope_id="sc1")

    # 1. Invalid queries and limits
    with pytest.raises(ValueError, match="Retrieval query must not be empty"):
        await service.search(session, query="   ", filters=filters)

    with pytest.raises(ValueError, match="limit must be between 1 and 20"):
        await service.search(session, query="valid", filters=filters, limit=0)

    # 2. Embedding error with on_embedding_error=False
    mock_embedding.embed_query.side_effect = EmbeddingProviderError("embedding failure")
    with pytest.raises(EmbeddingProviderError):
        await service.search(session, query="valid", filters=filters)

    # 3. OperationalError with on_vector_error=False
    mock_embedding.embed_query.side_effect = None
    mock_embedding.embed_query.return_value = [0.1] * 1536
    mock_repo.semantic_search = AsyncMock(side_effect=OperationalError("db error", {}, Exception()))
    with pytest.raises(OperationalError):
        await service.search(session, query="valid", filters=filters)

    # 4. Programming / unexpected error
    mock_repo.semantic_search = AsyncMock(side_effect=KeyError("unexpected"))
    with pytest.raises(KeyError):
        await service.search(session, query="valid", filters=filters)

    # 5. Empty hits with on_no_vector_hits=False
    mock_repo.semantic_search = AsyncMock(return_value=[])
    res_no_hits = await service.search(session, query="valid", filters=filters)
    assert res_no_hits.mode == "semantic"
    assert res_no_hits.hits == []
    assert res_no_hits.fallback_reason is None

    # 6. fetch_approved_chunks success
    hit = _make_hit(chunk_id="chk_01")
    mock_repo.fetch_approved_chunks = AsyncMock(return_value=[hit])
    found_chunks = await service.fetch_approved_chunks(session, chunk_ids=["chk_01", "chk_01"], filters=filters)
    assert len(found_chunks) == 1
    assert found_chunks[0].chunk_id == "chk_01"


@pytest.mark.asyncio
async def test_indexing_service_branches():
    from app.services.semantic_retrieval.indexing import (
        RetrievalIndexingService,
        SourceDocumentInput,
        SourceChunkInput,
    )

    bad_embed = MagicMock()
    bad_embed.dimensions = 512
    with pytest.raises(ValueError, match="dimension does not match"):
        RetrievalIndexingService(embedding_provider=bad_embed)

    good_embed = MagicMock()
    good_embed.dimensions = 1536
    good_embed.model = "model-1"
    good_embed.version = "v1"
    good_embed.embed = AsyncMock(return_value=[[0.1] * 1536])
    service = RetrievalIndexingService(embedding_provider=good_embed)
    session = AsyncMock()

    def _make_doc(**overrides: Any) -> SourceDocumentInput:
        data: dict[str, Any] = {
            "document_id": "d1",
            "document_version_id": "v1",
            "title": "Title",
            "scope_id": "sc1",
            "caps_ref": "4.M.1",
            "grade": 4,
            "subject_code": "MATH",
            "language": "en",
            "status": "approved",
            "permission_scope": "public",
            "license_status": "open",
            "quality_score": 0.9,
        }
        data.update(overrides)
        return SourceDocumentInput(**cast(Any, data))

    doc = _make_doc()

    # Empty chunks
    with pytest.raises(ValueError, match="at least one chunk"):
        await service.upsert_document(session, document=doc, chunks=[])

    # Validation errors
    doc_bad_id = _make_doc(document_id="", document_version_id="")
    with pytest.raises(ValueError, match="Document and version identifiers"):
        await service.upsert_document(session, document=doc_bad_id, chunks=[SourceChunkInput("c1", 0, "content")])

    doc_bad_title = _make_doc(scope_id="", title="")
    with pytest.raises(ValueError, match="Document scope and title"):
        await service.upsert_document(session, document=doc_bad_title, chunks=[SourceChunkInput("c1", 0, "content")])

    doc_bad_qs = _make_doc(quality_score=1.5)
    with pytest.raises(ValueError, match="quality score must be between zero and one"):
        await service.upsert_document(session, document=doc_bad_qs, chunks=[SourceChunkInput("c1", 0, "content")])

    doc_bad_lic = _make_doc(status="approved", license_status="")
    with pytest.raises(ValueError, match="approved license status"):
        await service.upsert_document(session, document=doc_bad_lic, chunks=[SourceChunkInput("c1", 0, "content")])

    # reindex_document: no rows
    mock_res_empty = MagicMock()
    mock_res_empty.mappings.return_value.all.return_value = []
    session.execute.return_value = mock_res_empty
    assert await service.reindex_document(session, document_id="d1") == 0

    # reindex_document: with rows
    mock_res_rows = MagicMock()
    mock_res_rows.mappings.return_value.all.return_value = [{"chunk_id": "c1", "content": "Text content"}]
    session.execute.return_value = mock_res_rows
    reindexed = await service.reindex_document(session, document_id="d1")
    assert reindexed == 1
    assert good_embed.embed.called

