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


def _make_hit(**kwargs) -> RetrievalHit:
    hit_data = {
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
    return RetrievalHit(**hit_data)


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
