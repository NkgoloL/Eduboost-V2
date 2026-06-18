"""Real-corpus retrieval evaluation helpers for Phase 2R Gate 2R.8."""
from __future__ import annotations

from dataclasses import dataclass, field


class EvaluationRejectedError(ValueError):
    pass


@dataclass(frozen=True)
class RetrievalEvaluationCase:
    case_id: str
    language: str
    strand: str
    term: int | None
    query: str
    expected_chunk_ids: list[str] = field(default_factory=list)
    retrieved_chunk_ids: list[str] = field(default_factory=list)
    is_negative_case: bool = False
    prohibited_hit_count: int = 0
    wrong_version_hit_count: int = 0
    wrong_language_hit_count: int = 0


@dataclass(frozen=True)
class RetrievalMetrics:
    recall_at_k: float
    precision_at_k: float
    mrr: float
    prohibited_hit_count: int
    wrong_version_hit_count: int
    wrong_language_hit_count: int
    case_count: int
    positive_case_count: int
    negative_case_count: int


class RetrievalEvaluationScorer:
    def score(self, cases: list[RetrievalEvaluationCase], *, k: int = 5) -> RetrievalMetrics:
        if not cases:
            raise EvaluationRejectedError("evaluation dataset is empty")
        recall_sum = 0.0
        precision_sum = 0.0
        reciprocal_sum = 0.0
        positive = 0
        negative = 0
        for case in cases:
            hits = case.retrieved_chunk_ids[:k]
            if case.is_negative_case:
                negative += 1
                if hits:
                    # Negative cases should not retrieve authoritative content.
                    precision_sum += 0.0
                continue
            positive += 1
            expected = set(case.expected_chunk_ids)
            if not expected:
                raise EvaluationRejectedError(f"positive case {case.case_id} has no expected chunks")
            matched = [chunk_id for chunk_id in hits if chunk_id in expected]
            recall_sum += len(set(matched)) / len(expected)
            precision_sum += len(matched) / max(len(hits), 1)
            for rank, chunk_id in enumerate(hits, start=1):
                if chunk_id in expected:
                    reciprocal_sum += 1 / rank
                    break
        if positive < 18:
            raise EvaluationRejectedError("real-corpus evaluation requires at least 18 positive cases")
        if negative < 10:
            raise EvaluationRejectedError("real-corpus evaluation requires at least 10 negative cases")
        prohibited = sum(case.prohibited_hit_count for case in cases)
        wrong_version = sum(case.wrong_version_hit_count for case in cases)
        wrong_language = sum(case.wrong_language_hit_count for case in cases)
        if prohibited or wrong_version or wrong_language:
            raise EvaluationRejectedError("blocked, wrong-version, or wrong-language authoritative hits are not allowed")
        return RetrievalMetrics(
            recall_at_k=recall_sum / positive,
            precision_at_k=precision_sum / positive,
            mrr=reciprocal_sum / positive,
            prohibited_hit_count=prohibited,
            wrong_version_hit_count=wrong_version,
            wrong_language_hit_count=wrong_language,
            case_count=len(cases),
            positive_case_count=positive,
            negative_case_count=negative,
        )
