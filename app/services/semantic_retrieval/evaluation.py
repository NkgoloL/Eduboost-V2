"""Retrieval evaluation metrics and closure thresholds."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.semantic_retrieval.service import SemanticRetrievalService
from app.services.semantic_retrieval.types import EvaluationCase, EvaluationMetrics


async def evaluate_retrieval(
    session: AsyncSession,
    *,
    service: SemanticRetrievalService,
    cases: list[EvaluationCase],
    recall_threshold: float = 0.80,
    mrr_threshold: float = 0.60,
    unsafe_hit_threshold: int = 0,
) -> EvaluationMetrics:
    if not cases:
        raise ValueError("Retrieval evaluation requires at least one case.")
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    precisions: list[float] = []
    unsafe_hit_count = 0
    case_results: list[dict[str, object]] = []

    for case in cases:
        result = await service.search(
            session,
            query=case.query,
            filters=case.filters,
            limit=case.k,
        )
        returned = [hit.chunk_id for hit in result.hits]
        expected = set(case.expected_chunk_ids)
        matches = [chunk_id for chunk_id in returned if chunk_id in expected]
        recall = len(set(matches)) / len(expected) if expected else 1.0
        precision = len(matches) / case.k
        first_rank = next(
            (rank for rank, chunk_id in enumerate(returned, 1) if chunk_id in expected),
            None,
        )
        reciprocal_rank = 1 / first_rank if first_rank else 0.0
        unsafe = sum(
            1
            for hit in result.hits
            if hit.document_status not in {"approved", "indexed", "training_ready"}
            or hit.chunk_status not in {"approved", "indexed", "training_ready"}
        )
        unsafe_hit_count += unsafe
        recalls.append(recall)
        precisions.append(precision)
        reciprocal_ranks.append(reciprocal_rank)
        case_results.append(
            {
                "case_id": case.case_id,
                "mode": result.mode,
                "returned_chunk_ids": returned,
                "expected_chunk_ids": sorted(expected),
                "recall_at_k": recall,
                "precision_at_k": precision,
                "reciprocal_rank": reciprocal_rank,
                "fallback_reason": result.fallback_reason,
                "unsafe_hit_count": unsafe,
            }
        )

    recall_at_k = sum(recalls) / len(recalls)
    mean_reciprocal_rank = sum(reciprocal_ranks) / len(reciprocal_ranks)
    precision_at_k = sum(precisions) / len(precisions)
    passed = (
        recall_at_k >= recall_threshold
        and mean_reciprocal_rank >= mrr_threshold
        and unsafe_hit_count <= unsafe_hit_threshold
    )
    return EvaluationMetrics(
        case_count=len(cases),
        recall_at_k=recall_at_k,
        mean_reciprocal_rank=mean_reciprocal_rank,
        precision_at_k=precision_at_k,
        unsafe_hit_count=unsafe_hit_count,
        passed=passed,
        thresholds={
            "recall_at_k": recall_threshold,
            "mean_reciprocal_rank": mrr_threshold,
            "unsafe_hit_count": float(unsafe_hit_threshold),
        },
        case_results=case_results,
    )
