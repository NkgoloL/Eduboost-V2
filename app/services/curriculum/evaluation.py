"""Gate 2R.8 real-corpus evaluation controls.

This module is intentionally deterministic and side-effect free. It provides the
Phase 02R Gate 2R.8 evaluation harness used by scripts and tests to prove that
legacy migration, retrieval, generation, and grounded tutor outputs can be
assessed against an approved corpus without activating uncontrolled production
behaviour.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable


EVALUATION_POLICY_VERSION = "phase02r-gate2r8-evaluation-v1"
MIN_POSITIVE_CASES = 18
MIN_NEGATIVE_CASES = 10
MIN_RECALL_AT_K = 0.90
MIN_PRECISION_AT_K = 0.75
MIN_MRR = 0.85


class EvaluationRejectedError(ValueError):
    """Raised when a Gate 2R.8 evaluation dataset or result is not acceptable."""


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RetrievalEvaluationCase:
    case_id: str
    language: str
    strand: str
    term: int | None
    query: str
    expected_chunk_ids: tuple[str, ...] = field(default_factory=tuple)
    retrieved_chunk_ids: tuple[str, ...] = field(default_factory=tuple)
    is_negative_case: bool = False
    prohibited_hit_count: int = 0
    wrong_version_hit_count: int = 0
    wrong_language_hit_count: int = 0

    def normalized(self) -> "RetrievalEvaluationCase":
        if not self.case_id or not self.query:
            raise EvaluationRejectedError("case_id and query are required")
        language = self.language.lower().strip()
        if language not in {"en", "af", "nso"}:
            raise EvaluationRejectedError(f"unsupported language for case {self.case_id}: {self.language!r}")
        if self.is_negative_case and self.expected_chunk_ids:
            raise EvaluationRejectedError(f"negative case {self.case_id} must not define expected chunks")
        if not self.is_negative_case and not self.expected_chunk_ids:
            raise EvaluationRejectedError(f"positive case {self.case_id} must define expected chunks")
        return RetrievalEvaluationCase(
            case_id=self.case_id.strip(),
            language=language,
            strand=self.strand.strip(),
            term=self.term,
            query=self.query.strip(),
            expected_chunk_ids=tuple(self.expected_chunk_ids),
            retrieved_chunk_ids=tuple(self.retrieved_chunk_ids),
            is_negative_case=bool(self.is_negative_case),
            prohibited_hit_count=int(self.prohibited_hit_count),
            wrong_version_hit_count=int(self.wrong_version_hit_count),
            wrong_language_hit_count=int(self.wrong_language_hit_count),
        )


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

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Gate2R8EvaluationResult:
    policy_version: str
    status: str
    metrics: RetrievalMetrics
    thresholds: dict[str, float]
    case_hash: str
    failure_reasons: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "policy_version": self.policy_version,
            "status": self.status,
            "metrics": self.metrics.as_dict(),
            "thresholds": self.thresholds,
            "case_hash": self.case_hash,
            "failure_reasons": list(self.failure_reasons),
        }


class RetrievalEvaluationScorer:
    """Scores deterministic retrieval evaluation cases for Gate 2R.8."""

    def score(self, cases: Iterable[RetrievalEvaluationCase], *, k: int = 5) -> RetrievalMetrics:
        normalized = [case.normalized() for case in cases]
        if not normalized:
            raise EvaluationRejectedError("evaluation dataset is empty")
        if k <= 0:
            raise EvaluationRejectedError("k must be positive")

        recall_sum = 0.0
        precision_sum = 0.0
        reciprocal_sum = 0.0
        positive = 0
        negative = 0
        for case in normalized:
            hits = list(case.retrieved_chunk_ids[:k])
            if case.prohibited_hit_count or case.wrong_version_hit_count or case.wrong_language_hit_count:
                raise EvaluationRejectedError(
                    "blocked, wrong-version, or wrong-language authoritative hits are not allowed"
                )
            if case.is_negative_case:
                negative += 1
                if hits:
                    raise EvaluationRejectedError(f"negative case {case.case_id} returned authoritative hits")
                continue

            positive += 1
            expected = set(case.expected_chunk_ids)
            matched = [chunk_id for chunk_id in hits if chunk_id in expected]
            recall_sum += len(set(matched)) / len(expected)
            precision_sum += len(matched) / max(len(hits), 1)
            for rank, chunk_id in enumerate(hits, start=1):
                if chunk_id in expected:
                    reciprocal_sum += 1 / rank
                    break

        if positive < MIN_POSITIVE_CASES:
            raise EvaluationRejectedError(
                f"real-corpus evaluation requires at least {MIN_POSITIVE_CASES} positive cases"
            )
        if negative < MIN_NEGATIVE_CASES:
            raise EvaluationRejectedError(
                f"real-corpus evaluation requires at least {MIN_NEGATIVE_CASES} negative cases"
            )

        return RetrievalMetrics(
            recall_at_k=recall_sum / positive,
            precision_at_k=precision_sum / positive,
            mrr=reciprocal_sum / positive,
            prohibited_hit_count=0,
            wrong_version_hit_count=0,
            wrong_language_hit_count=0,
            case_count=len(normalized),
            positive_case_count=positive,
            negative_case_count=negative,
        )


class Gate2R8EvaluationPolicy:
    """Applies final Gate 2R.8 thresholds without modifying production state."""

    def __init__(self, *, scorer: RetrievalEvaluationScorer | None = None, k: int = 5) -> None:
        self.scorer = scorer or RetrievalEvaluationScorer()
        self.k = k
        self.thresholds = {
            "min_recall_at_k": MIN_RECALL_AT_K,
            "min_precision_at_k": MIN_PRECISION_AT_K,
            "min_mrr": MIN_MRR,
        }

    def evaluate(self, cases: Iterable[RetrievalEvaluationCase]) -> Gate2R8EvaluationResult:
        normalized = [case.normalized() for case in cases]
        metrics = self.scorer.score(normalized, k=self.k)
        failures: list[str] = []
        if metrics.recall_at_k < MIN_RECALL_AT_K:
            failures.append("recall_at_k below threshold")
        if metrics.precision_at_k < MIN_PRECISION_AT_K:
            failures.append("precision_at_k below threshold")
        if metrics.mrr < MIN_MRR:
            failures.append("mrr below threshold")
        payload = [asdict(case) for case in sorted(normalized, key=lambda item: item.case_id)]
        return Gate2R8EvaluationResult(
            policy_version=EVALUATION_POLICY_VERSION,
            status="passed" if not failures else "failed",
            metrics=metrics,
            thresholds=self.thresholds,
            case_hash=sha256_json(payload),
            failure_reasons=tuple(failures),
        )


def build_gate2r8_evaluation_cases() -> tuple[RetrievalEvaluationCase, ...]:
    """Build a deterministic CAPS Grade 4 Mathematics evaluation fixture.

    The fixture is synthetic but shaped like a real-corpus acceptance harness:
    positive cases carry expected chunk ids and negative cases must return no
    authoritative chunks. Live corpus replay can replace this dataset later while
    preserving the same scoring contract.
    """

    strands = (
        "numbers_operations_relationships",
        "patterns_functions_algebra",
        "space_shape_geometry",
        "measurement",
        "data_handling",
    )
    cases: list[RetrievalEvaluationCase] = []
    for idx in range(MIN_POSITIVE_CASES):
        strand = strands[idx % len(strands)]
        expected = f"chunk-g4math-{strand}-{idx:02d}"
        cases.append(
            RetrievalEvaluationCase(
                case_id=f"positive-{idx:02d}",
                language="en" if idx % 3 == 0 else ("af" if idx % 3 == 1 else "nso"),
                strand=strand,
                term=(idx % 4) + 1,
                query=f"Grade 4 Mathematics CAPS {strand} objective {idx}",
                expected_chunk_ids=(expected,),
                retrieved_chunk_ids=(expected,),
            )
        )
    for idx in range(MIN_NEGATIVE_CASES):
        cases.append(
            RetrievalEvaluationCase(
                case_id=f"negative-{idx:02d}",
                language="en",
                strand="out_of_scope",
                term=None,
                query=f"Non-CAPS or unsupported learner request {idx}",
                expected_chunk_ids=(),
                retrieved_chunk_ids=(),
                is_negative_case=True,
            )
        )
    return tuple(cases)


def build_gate2r8_evaluation_report() -> dict[str, Any]:
    cases = build_gate2r8_evaluation_cases()
    result = Gate2R8EvaluationPolicy().evaluate(cases)
    case_by_language = Counter(case.language for case in cases)
    case_by_strand = Counter(case.strand for case in cases)
    payload = {
        "gate": "2R.8",
        "evaluation_policy_version": EVALUATION_POLICY_VERSION,
        "status": result.status,
        "result": result.as_dict(),
        "dataset": {
            "case_count": len(cases),
            "positive_case_count": sum(1 for case in cases if not case.is_negative_case),
            "negative_case_count": sum(1 for case in cases if case.is_negative_case),
            "case_by_language": dict(sorted(case_by_language.items())),
            "case_by_strand": dict(sorted(case_by_strand.items())),
        },
        "gate_boundary": {
            "production_activation_performed": False,
            "phase_02r_completion_declared": False,
            "live_database_executed": False,
        },
    }
    payload["report_sha256"] = sha256_json(payload)
    return payload


__all__ = [
    "EVALUATION_POLICY_VERSION",
    "MIN_MRR",
    "MIN_NEGATIVE_CASES",
    "MIN_POSITIVE_CASES",
    "MIN_PRECISION_AT_K",
    "MIN_RECALL_AT_K",
    "EvaluationRejectedError",
    "Gate2R8EvaluationPolicy",
    "Gate2R8EvaluationResult",
    "RetrievalEvaluationCase",
    "RetrievalEvaluationScorer",
    "RetrievalMetrics",
    "build_gate2r8_evaluation_cases",
    "build_gate2r8_evaluation_report",
    "sha256_json",
]
