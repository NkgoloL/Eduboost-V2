"""Approved corpus and atomic activation helpers for Phase 2R Gate 2R.5."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


class CorpusRejectedError(ValueError):
    pass


@dataclass(frozen=True)
class CorpusChunkCandidate:
    chunk_version_id: str
    source_version_id: str
    mapping_version_id: str
    authority_tier: str
    rights_status: str
    chunk_review_status: str
    mapping_review_status: str
    quality_score: float
    language: str


@dataclass(frozen=True)
class CorpusManifest:
    corpus_code: str
    version_number: int
    scope: dict[str, Any]
    language: str
    source_version_ids: list[str]
    chunk_version_ids: list[str]
    mapping_version_ids: list[str]
    embedding_model: str
    embedding_version: str
    manifest_sha256: str


class CorpusBuilder:
    """Build a deterministic manifest from approved chunk candidates."""

    def build_manifest(
        self,
        *,
        corpus_code: str,
        version_number: int,
        scope: dict[str, Any],
        language: str,
        embedding_model: str,
        embedding_version: str,
        candidates: list[CorpusChunkCandidate],
    ) -> CorpusManifest:
        if language not in {"en", "af", "nso"}:
            raise CorpusRejectedError("invalid corpus language")
        eligible = [self._require_eligible(candidate, language=language) for candidate in candidates]
        if not eligible:
            raise CorpusRejectedError("corpus requires at least one approved candidate")
        if not any(candidate.authority_tier == "tier_1" for candidate in eligible):
            raise CorpusRejectedError("corpus requires Tier 1 authority coverage")
        source_ids = sorted({candidate.source_version_id for candidate in eligible})
        chunk_ids = sorted(candidate.chunk_version_id for candidate in eligible)
        mapping_ids = sorted(candidate.mapping_version_id for candidate in eligible)
        payload = {
            "corpus_code": corpus_code,
            "version_number": version_number,
            "scope": scope,
            "language": language,
            "source_version_ids": source_ids,
            "chunk_version_ids": chunk_ids,
            "mapping_version_ids": mapping_ids,
            "embedding_model": embedding_model,
            "embedding_version": embedding_version,
        }
        manifest_sha = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return CorpusManifest(
            corpus_code=corpus_code,
            version_number=version_number,
            scope=scope,
            language=language,
            source_version_ids=source_ids,
            chunk_version_ids=chunk_ids,
            mapping_version_ids=mapping_ids,
            embedding_model=embedding_model,
            embedding_version=embedding_version,
            manifest_sha256=manifest_sha,
        )

    @staticmethod
    def _require_eligible(candidate: CorpusChunkCandidate, *, language: str) -> CorpusChunkCandidate:
        if candidate.language != language:
            raise CorpusRejectedError("candidate language does not match corpus language")
        if candidate.rights_status not in {"approved", "approved_with_conditions"}:
            raise CorpusRejectedError("candidate rights are not approved")
        if candidate.chunk_review_status != "approved":
            raise CorpusRejectedError("candidate chunk is not extraction-reviewed and approved")
        if candidate.mapping_review_status != "approved":
            raise CorpusRejectedError("candidate mapping is not approved")
        if candidate.authority_tier not in {"tier_1", "tier_2", "tier_3"}:
            raise CorpusRejectedError("candidate authority tier is invalid")
        if candidate.quality_score < 0.75:
            raise CorpusRejectedError("candidate quality score is below the retrieval threshold")
        return candidate


@dataclass(frozen=True)
class ActivationPlan:
    activation_key: str
    corpus_version_id: str
    previous_corpus_version_id: str | None
    binding_epoch: int
    outbox_events: list[dict[str, Any]] = field(default_factory=list)


class CorpusActivationPlanner:
    """Create an activation plan that must be committed in one DB transaction.

    Database changes are the only atomic part. Cache invalidation, metrics and
    event publication must be written to a transactional outbox and delivered by
    an idempotent worker after commit.
    """

    @staticmethod
    def plan_activation(
        *,
        activation_key: str,
        corpus_version_id: str,
        previous_corpus_version_id: str | None,
        current_epoch: int,
    ) -> ActivationPlan:
        if not activation_key or ":" not in activation_key:
            raise CorpusRejectedError("activation_key must encode scope and language")
        next_epoch = current_epoch + 1
        if next_epoch <= 0:
            raise CorpusRejectedError("binding epoch must be positive")
        return ActivationPlan(
            activation_key=activation_key,
            corpus_version_id=corpus_version_id,
            previous_corpus_version_id=previous_corpus_version_id,
            binding_epoch=next_epoch,
            outbox_events=[
                {"event_type": "corpus.cache.invalidate", "activation_key": activation_key, "binding_epoch": next_epoch},
                {"event_type": "corpus.metrics.publish", "activation_key": activation_key, "corpus_version_id": corpus_version_id},
            ],
        )


def versioned_cache_key(*, activation_key: str, corpus_version_id: str, binding_epoch: int) -> str:
    if binding_epoch <= 0:
        raise CorpusRejectedError("binding_epoch must be positive")
    return f"phase02r:corpus:{activation_key}:{corpus_version_id}:epoch:{binding_epoch}"
