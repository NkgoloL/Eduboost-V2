from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.services.semantic_retrieval.evaluation import evaluate_retrieval
from app.services.semantic_retrieval.types import (
    EvaluationCase,
    RetrievalFilters,
    RetrievalHit,
    RetrievalResult,
)


FILTERS = RetrievalFilters(scope_id="g4-math", caps_ref="4.M.1.1")


def make_hit(chunk_id: str) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        document_id="doc",
        document_version_id="v1",
        title="Title",
        content="Text",
        heading=None,
        section_path=None,
        page_start=None,
        page_end=None,
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
        source_hash="source",
        chunk_hash="chunk",
        curriculum_mapping_id=None,
        score=1.0,
        retrieval_mode="semantic",
    )


@dataclass
class FakeService:
    results: dict[str, list[str]]

    async def search(self, session, *, query, filters, limit):
        return RetrievalResult(
            query_fingerprint="fingerprint",
            mode="semantic",
            hits=[make_hit(chunk_id) for chunk_id in self.results[query]][:limit],
            fallback_reason=None,
            embedding_model="fake",
            embedding_version="1",
            elapsed_ms=1.0,
        )


@pytest.mark.asyncio
async def test_evaluation_computes_recall_mrr_and_gate() -> None:
    cases = [
        EvaluationCase(
            case_id="one",
            query="whole numbers",
            expected_chunk_ids=frozenset({"a"}),
            filters=FILTERS,
            k=2,
        ),
        EvaluationCase(
            case_id="two",
            query="place value",
            expected_chunk_ids=frozenset({"b"}),
            filters=FILTERS,
            k=2,
        ),
    ]
    metrics = await evaluate_retrieval(
        object(),
        service=FakeService({"whole numbers": ["a", "x"], "place value": ["x", "b"]}),  # type: ignore[arg-type]
        cases=cases,
        recall_threshold=1.0,
        mrr_threshold=0.75,
    )
    assert metrics.recall_at_k == 1.0
    assert metrics.mean_reciprocal_rank == 0.75
    assert metrics.passed
