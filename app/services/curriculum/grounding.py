"""Grounding sufficiency rules for Phase 2R Gate 2R.6."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


class GroundingRejectedError(ValueError):
    pass


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_version_id: str
    source_version_id: str
    mapping_version_ids: list[str]
    objective_ids: list[str]
    authority_tier: str
    rights_status: str
    review_status: str
    corpus_version_id: str
    score: float
    language: str
    text: str


@dataclass(frozen=True)
class GroundingDecision:
    passed: bool
    status: str
    source_snapshot_hash: str | None
    chunk_version_ids: list[str] = field(default_factory=list)
    source_version_ids: list[str] = field(default_factory=list)
    mapping_version_ids: list[str] = field(default_factory=list)
    failure_reasons: list[str] = field(default_factory=list)


class GroundingPolicyEngine:
    def validate_generation_grounding(
        self,
        *,
        corpus_version_id: str | None,
        requested_objective_ids: list[str],
        retrieved_chunks: list[RetrievedChunk],
    ) -> GroundingDecision:
        reasons: list[str] = []
        if not corpus_version_id:
            reasons.append("active_corpus_version_missing")
        if not requested_objective_ids:
            reasons.append("requested_objectives_missing")
        if not retrieved_chunks:
            reasons.append("retrieved_chunks_missing")
        if retrieved_chunks and not any(chunk.authority_tier == "tier_1" for chunk in retrieved_chunks):
            reasons.append("tier_1_grounding_missing")
        for chunk in retrieved_chunks:
            if chunk.corpus_version_id != corpus_version_id:
                reasons.append("mixed_corpus_version")
            if chunk.rights_status not in {"approved", "approved_with_conditions"}:
                reasons.append("rights_not_approved")
            if chunk.review_status != "approved":
                reasons.append("chunk_not_approved")
        covered = {objective for chunk in retrieved_chunks for objective in chunk.objective_ids}
        missing_objectives = sorted(set(requested_objective_ids) - covered)
        if missing_objectives:
            reasons.append("objective_coverage_incomplete:" + ",".join(missing_objectives))
        if reasons:
            return GroundingDecision(False, "failed", None, failure_reasons=sorted(set(reasons)))
        payload = [
            {
                "chunk_version_id": chunk.chunk_version_id,
                "source_version_id": chunk.source_version_id,
                "mapping_version_ids": sorted(chunk.mapping_version_ids),
                "score": chunk.score,
                "text_sha256": hashlib.sha256(chunk.text.encode()).hexdigest(),
            }
            for chunk in sorted(retrieved_chunks, key=lambda item: item.chunk_version_id)
        ]
        snapshot = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return GroundingDecision(
            True,
            "passed",
            snapshot,
            chunk_version_ids=sorted(chunk.chunk_version_id for chunk in retrieved_chunks),
            source_version_ids=sorted({chunk.source_version_id for chunk in retrieved_chunks}),
            mapping_version_ids=sorted({mapping for chunk in retrieved_chunks for mapping in chunk.mapping_version_ids}),
        )


def require_grounded_or_safe_fallback(decision: GroundingDecision, *, fallback_reason: str | None = None) -> None:
    if decision.passed:
        return
    if not fallback_reason:
        raise GroundingRejectedError("curriculum response requires grounding or explicit safe fallback")
