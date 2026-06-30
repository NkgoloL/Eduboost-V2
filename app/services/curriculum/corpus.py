"""Approved semantic corpus and real-source retrieval controls for Phase 2R Gate 2R.5."""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Sequence

SUPPORTED_LANGUAGES = {"en", "af", "nso"}
APPROVED_RIGHTS = {"approved", "approved_with_conditions"}
APPROVED_REVIEW = "approved"
APPROVED_SOURCE_STATUSES = {"active", "approved"}
AUTHORITY_TIERS = {"tier_1", "tier_2", "tier_3"}
OFFICIAL_AUTHORITY_STATUSES = {"official_source", "approved_human_translation"}
FORBIDDEN_AUTHORITY_STATUSES = {"machine_translation_draft", "generated_learner_explanation"}
RETRIEVAL_POLICY_VERSION = "phase02r-gate2r5-retrieval-v1"
CORPUS_POLICY_VERSION = "phase02r-gate2r5-corpus-v1"


class CorpusRejectedError(ValueError):
    """Raised when Gate 2R.5 corpus/retrieval policy rejects a record."""


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _require_non_empty(value: str | None, field_name: str) -> str:
    if not value or not str(value).strip():
        raise CorpusRejectedError(f"{field_name} is required")
    return str(value)


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token}


def build_activation_key(
    *,
    curriculum_code: str = "CAPS",
    grade: int = 4,
    subject_code: str = "MATH",
    delivery_language: str = "en",
    tenant_scope: str = "global",
) -> str:
    if delivery_language not in SUPPORTED_LANGUAGES:
        raise CorpusRejectedError("unsupported delivery language")
    if grade <= 0:
        raise CorpusRejectedError("grade must be positive")
    parts = [curriculum_code.upper(), f"g{grade}", subject_code.upper(), delivery_language, tenant_scope]
    if any(not part or ":" in part for part in parts):
        raise CorpusRejectedError("activation key parts must be non-empty and must not contain ':'")
    return ":".join(parts)


def parse_activation_key(activation_key: str) -> dict[str, Any]:
    parts = activation_key.split(":")
    if len(parts) != 5:
        raise CorpusRejectedError("activation_key must contain curriculum, grade, subject, language, tenant")
    curriculum_code, grade_part, subject_code, language, tenant_scope = parts
    if not grade_part.startswith("g") or not grade_part[1:].isdigit():
        raise CorpusRejectedError("activation_key grade must be encoded as g<number>")
    if language not in SUPPORTED_LANGUAGES:
        raise CorpusRejectedError("activation_key language is unsupported")
    return {
        "curriculum_code": curriculum_code,
        "grade": int(grade_part[1:]),
        "subject_code": subject_code,
        "delivery_language": language,
        "tenant_scope": tenant_scope,
    }


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
    curriculum_node_version_id: str | None = None
    source_page_id: str | None = None
    source_section_id: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    text_sha256: str | None = None
    retrieval_text: str | None = None
    source_status: str = "active"
    source_sha256: str | None = None
    original_object_sha256: str | None = None
    extraction_review_status: str = "approved"
    language_status: str = "official_source"
    support_type: str = "assesses"
    rights_use: str = "retrieval"
    may_use_for_retrieval: bool = True
    may_embed: bool = True
    unresolved_security_warnings: tuple[str, ...] = field(default_factory=tuple)
    synthetic_fixture: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def normalized(self) -> "CorpusChunkCandidate":
        return replace(
            self,
            chunk_version_id=_require_non_empty(self.chunk_version_id, "chunk_version_id"),
            source_version_id=_require_non_empty(self.source_version_id, "source_version_id"),
            mapping_version_id=_require_non_empty(self.mapping_version_id, "mapping_version_id"),
            authority_tier=self.authority_tier.lower(),
            rights_status=self.rights_status.lower(),
            chunk_review_status=self.chunk_review_status.lower(),
            mapping_review_status=self.mapping_review_status.lower(),
            extraction_review_status=self.extraction_review_status.lower(),
            language=self.language.lower(),
            language_status=self.language_status.lower(),
            source_status=self.source_status.lower(),
            metadata=dict(sorted(self.metadata.items())),
        )


@dataclass(frozen=True)
class EligibilityDecision:
    candidate: CorpusChunkCandidate
    eligible: bool
    reasons: tuple[str, ...]

    def require_eligible(self) -> CorpusChunkCandidate:
        if not self.eligible:
            raise CorpusRejectedError("candidate is not corpus eligible: " + "; ".join(self.reasons))
        return self.candidate


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
    activation_key: str | None = None
    corpus_policy_version: str = CORPUS_POLICY_VERSION
    retrieval_policy_version: str = RETRIEVAL_POLICY_VERSION
    curriculum_node_version_ids: list[str] = field(default_factory=list)
    membership_count: int = 0
    tier1_membership_count: int = 0
    source_snapshot_hash: str | None = None
    retrieval_projection_sha256: str | None = None
    status: str = "built"
    review_status: str = "review_required"

    def export(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FrozenCorpusPackage:
    manifest: CorpusManifest
    candidates: tuple[CorpusChunkCandidate, ...]
    freeze_sha256: str

    def export(self) -> dict[str, Any]:
        return {
            "manifest": self.manifest.export(),
            "candidates": [asdict(candidate.normalized()) for candidate in self.candidates],
            "freeze_sha256": self.freeze_sha256,
        }


class CorpusBuilder:
    def evaluate_candidate(self, candidate: CorpusChunkCandidate, *, language: str) -> EligibilityDecision:
        c = candidate.normalized()
        reasons: list[str] = []
        if c.language != language:
            reasons.append("candidate language does not match corpus language")
        if c.language not in SUPPORTED_LANGUAGES:
            reasons.append("candidate language is unsupported")
        if c.rights_status not in APPROVED_RIGHTS:
            reasons.append("candidate rights are not approved")
        if not c.may_use_for_retrieval:
            reasons.append("candidate is not approved for retrieval use")
        if not c.may_embed:
            reasons.append("candidate is not approved for embedding/projection use")
        if c.source_status not in APPROVED_SOURCE_STATUSES:
            reasons.append("source version is not active/approved")
        if c.chunk_review_status != APPROVED_REVIEW:
            reasons.append("candidate chunk is not extraction-reviewed and approved")
        if c.extraction_review_status != APPROVED_REVIEW:
            reasons.append("candidate extraction is not approved")
        if c.mapping_review_status != APPROVED_REVIEW:
            reasons.append("candidate mapping is not approved")
        if c.authority_tier not in AUTHORITY_TIERS:
            reasons.append("candidate authority tier is invalid")
        if not math.isfinite(c.quality_score) or c.quality_score < 0.75:
            reasons.append("candidate quality score is below the retrieval threshold")
        if c.language_status in FORBIDDEN_AUTHORITY_STATUSES:
            reasons.append("machine/generated language status cannot be promoted to corpus authority")
        if c.language_status not in OFFICIAL_AUTHORITY_STATUSES:
            reasons.append("candidate language status is not authorised for corpus membership")
        if c.synthetic_fixture:
            reasons.append("synthetic fixture cannot enter approved corpus")
        if c.unresolved_security_warnings:
            reasons.append("candidate has unresolved security warnings")
        if c.page_start is not None and c.page_end is not None and c.page_end < c.page_start:
            reasons.append("candidate page range is invalid")
        if c.text_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", c.text_sha256):
            reasons.append("candidate text_sha256 must be a lowercase sha256")
        if c.retrieval_text is not None and not c.retrieval_text.strip():
            reasons.append("candidate retrieval_text is empty")
        return EligibilityDecision(c, not reasons, tuple(reasons))

    def build_manifest(
        self,
        *,
        corpus_code: str,
        version_number: int,
        scope: dict[str, Any],
        language: str,
        embedding_model: str,
        embedding_version: str,
        candidates: Sequence[CorpusChunkCandidate],
        activation_key: str | None = None,
        retrieval_policy_version: str = RETRIEVAL_POLICY_VERSION,
    ) -> CorpusManifest:
        if language not in SUPPORTED_LANGUAGES:
            raise CorpusRejectedError("invalid corpus language")
        if version_number <= 0:
            raise CorpusRejectedError("version_number must be positive")
        if not scope:
            raise CorpusRejectedError("scope is required")
        if activation_key is not None and parse_activation_key(activation_key)["delivery_language"] != language:
            raise CorpusRejectedError("activation_key language must match corpus language")
        eligible = [self.evaluate_candidate(candidate, language=language).require_eligible() for candidate in candidates]
        if not eligible:
            raise CorpusRejectedError("corpus requires at least one approved candidate")
        if not any(candidate.authority_tier == "tier_1" for candidate in eligible):
            raise CorpusRejectedError("corpus requires Tier 1 authority coverage")

        source_ids = sorted({candidate.source_version_id for candidate in eligible})
        chunk_ids = sorted(candidate.chunk_version_id for candidate in eligible)
        mapping_ids = sorted(candidate.mapping_version_id for candidate in eligible)
        node_ids = sorted({candidate.curriculum_node_version_id for candidate in eligible if candidate.curriculum_node_version_id})
        source_snapshot_hash = _sha256_json({
            "source_version_ids": source_ids,
            "chunk_version_ids": chunk_ids,
            "mapping_version_ids": mapping_ids,
            "curriculum_node_version_ids": node_ids,
        })
        payload = {
            "activation_key": activation_key,
            "corpus_code": corpus_code,
            "version_number": version_number,
            "scope": dict(sorted(scope.items())),
            "language": language,
            "source_version_ids": source_ids,
            "chunk_version_ids": chunk_ids,
            "mapping_version_ids": mapping_ids,
            "curriculum_node_version_ids": node_ids,
            "embedding_model": embedding_model,
            "embedding_version": embedding_version,
            "corpus_policy_version": CORPUS_POLICY_VERSION,
            "retrieval_policy_version": retrieval_policy_version,
            "source_snapshot_hash": source_snapshot_hash,
        }
        return CorpusManifest(
            corpus_code=corpus_code,
            version_number=version_number,
            scope=dict(sorted(scope.items())),
            language=language,
            source_version_ids=source_ids,
            chunk_version_ids=chunk_ids,
            mapping_version_ids=mapping_ids,
            embedding_model=embedding_model,
            embedding_version=embedding_version,
            manifest_sha256=_sha256_json(payload),
            activation_key=activation_key,
            retrieval_policy_version=retrieval_policy_version,
            curriculum_node_version_ids=node_ids,
            membership_count=len(eligible),
            tier1_membership_count=sum(1 for candidate in eligible if candidate.authority_tier == "tier_1"),
            source_snapshot_hash=source_snapshot_hash,
        )

    def freeze(self, *, manifest: CorpusManifest, candidates: Sequence[CorpusChunkCandidate]) -> FrozenCorpusPackage:
        normalized = tuple(sorted((candidate.normalized() for candidate in candidates), key=lambda c: (c.chunk_version_id, c.mapping_version_id)))
        if sorted(candidate.chunk_version_id for candidate in normalized) != manifest.chunk_version_ids:
            raise CorpusRejectedError("freeze candidates do not match manifest chunk membership")
        payload = {"manifest": manifest.export(), "candidates": [asdict(candidate) for candidate in normalized]}
        return FrozenCorpusPackage(manifest=manifest, candidates=normalized, freeze_sha256=_sha256_json(payload))

    @staticmethod
    def _require_eligible(candidate: CorpusChunkCandidate, *, language: str) -> CorpusChunkCandidate:
        return CorpusBuilder().evaluate_candidate(candidate, language=language).require_eligible()


@dataclass(frozen=True)
class CorpusRetrievalRecord:
    corpus_version_id: str
    activation_key: str
    binding_epoch: int
    chunk_version_id: str
    source_version_id: str
    mapping_version_id: str
    curriculum_node_version_id: str | None
    language: str
    authority_tier: str
    review_status: str
    rights_status: str
    quality_score: float
    retrieval_text: str
    page_start: int | None = None
    page_end: int | None = None
    text_sha256: str | None = None
    source_snapshot_hash: str | None = None

    def export(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetrievalProjection:
    corpus_version_id: str
    activation_key: str
    binding_epoch: int
    manifest_sha256: str
    retrieval_policy_version: str
    records: tuple[CorpusRetrievalRecord, ...]
    projection_sha256: str

    def export(self) -> dict[str, Any]:
        return {
            "corpus_version_id": self.corpus_version_id,
            "activation_key": self.activation_key,
            "binding_epoch": self.binding_epoch,
            "manifest_sha256": self.manifest_sha256,
            "retrieval_policy_version": self.retrieval_policy_version,
            "records": [record.export() for record in self.records],
            "projection_sha256": self.projection_sha256,
        }


class RetrievalProjectionBuilder:
    def build_projection(
        self,
        *,
        corpus_version_id: str,
        activation_key: str,
        binding_epoch: int,
        manifest: CorpusManifest,
        candidates: Sequence[CorpusChunkCandidate],
    ) -> RetrievalProjection:
        _require_non_empty(corpus_version_id, "corpus_version_id")
        if binding_epoch <= 0:
            raise CorpusRejectedError("binding_epoch must be positive")
        if manifest.activation_key and manifest.activation_key != activation_key:
            raise CorpusRejectedError("manifest activation_key does not match projection activation_key")
        if set(manifest.chunk_version_ids) != {candidate.normalized().chunk_version_id for candidate in candidates}:
            raise CorpusRejectedError("projection candidates must match manifest chunk membership exactly")
        parse_activation_key(activation_key)
        records = []
        builder = CorpusBuilder()
        for candidate in candidates:
            c = builder.evaluate_candidate(candidate, language=manifest.language).require_eligible()
            if c.chunk_version_id not in manifest.chunk_version_ids or c.mapping_version_id not in manifest.mapping_version_ids:
                raise CorpusRejectedError("candidate is outside frozen manifest membership")
            text = c.retrieval_text or f"{c.chunk_version_id} {c.curriculum_node_version_id or ''}"
            records.append(
                CorpusRetrievalRecord(
                    corpus_version_id=corpus_version_id,
                    activation_key=activation_key,
                    binding_epoch=binding_epoch,
                    chunk_version_id=c.chunk_version_id,
                    source_version_id=c.source_version_id,
                    mapping_version_id=c.mapping_version_id,
                    curriculum_node_version_id=c.curriculum_node_version_id,
                    language=c.language,
                    authority_tier=c.authority_tier,
                    review_status=c.chunk_review_status,
                    rights_status=c.rights_status,
                    quality_score=c.quality_score,
                    retrieval_text=text,
                    page_start=c.page_start,
                    page_end=c.page_end,
                    text_sha256=c.text_sha256,
                    source_snapshot_hash=manifest.source_snapshot_hash,
                )
            )
        records_tuple = tuple(sorted(records, key=lambda r: (r.chunk_version_id, r.mapping_version_id)))
        payload = {
            "corpus_version_id": corpus_version_id,
            "activation_key": activation_key,
            "binding_epoch": binding_epoch,
            "manifest_sha256": manifest.manifest_sha256,
            "retrieval_policy_version": manifest.retrieval_policy_version,
            "records": [record.export() for record in records_tuple],
        }
        return RetrievalProjection(
            corpus_version_id=corpus_version_id,
            activation_key=activation_key,
            binding_epoch=binding_epoch,
            manifest_sha256=manifest.manifest_sha256,
            retrieval_policy_version=manifest.retrieval_policy_version,
            records=records_tuple,
            projection_sha256=_sha256_json(payload),
        )


@dataclass(frozen=True)
class ActiveCorpusBinding:
    activation_key: str
    corpus_version_id: str
    binding_epoch: int
    manifest_sha256: str
    status: str = "active"


@dataclass(frozen=True)
class RetrievalQuery:
    activation_key: str
    corpus_version_id: str
    binding_epoch: int
    query_text: str
    language: str
    top_k: int = 5
    required_curriculum_node_version_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RetrievalHit:
    record: CorpusRetrievalRecord
    score: float
    matched_terms: tuple[str, ...]

    def export(self) -> dict[str, Any]:
        payload = self.record.export()
        payload.update({"score": self.score, "matched_terms": list(self.matched_terms)})
        return payload


@dataclass(frozen=True)
class RetrievalResult:
    query: RetrievalQuery
    hits: tuple[RetrievalHit, ...]
    source_snapshot_hash: str
    retrieval_policy_version: str = RETRIEVAL_POLICY_VERSION

    def export(self) -> dict[str, Any]:
        return {
            "query": asdict(self.query),
            "hits": [hit.export() for hit in self.hits],
            "source_snapshot_hash": self.source_snapshot_hash,
            "retrieval_policy_version": self.retrieval_policy_version,
        }


class ActiveCorpusRetriever:
    def __init__(self, projection: RetrievalProjection, binding: ActiveCorpusBinding) -> None:
        if binding.status != "active":
            raise CorpusRejectedError("binding is not active")
        if projection.activation_key != binding.activation_key:
            raise CorpusRejectedError("projection activation_key does not match active binding")
        if projection.corpus_version_id != binding.corpus_version_id:
            raise CorpusRejectedError("projection corpus_version_id does not match active binding")
        if projection.binding_epoch != binding.binding_epoch:
            raise CorpusRejectedError("projection binding_epoch does not match active binding")
        if projection.manifest_sha256 != binding.manifest_sha256:
            raise CorpusRejectedError("projection manifest_sha256 does not match active binding")
        self.projection = projection
        self.binding = binding

    def search(self, query: RetrievalQuery) -> RetrievalResult:
        if query.activation_key != self.binding.activation_key:
            raise CorpusRejectedError("query activation_key does not match active binding")
        if query.corpus_version_id != self.binding.corpus_version_id:
            raise CorpusRejectedError("query corpus_version_id does not match active binding")
        if query.binding_epoch != self.binding.binding_epoch:
            raise CorpusRejectedError("query binding_epoch is stale or wrong")
        if query.language not in SUPPORTED_LANGUAGES:
            raise CorpusRejectedError("query language is unsupported")
        if query.top_k <= 0:
            raise CorpusRejectedError("top_k must be positive")
        query_terms = _tokenize(query.query_text)
        if not query_terms:
            raise CorpusRejectedError("query_text must contain searchable terms")
        hits: list[RetrievalHit] = []
        for record in self.projection.records:
            if record.activation_key != query.activation_key or record.corpus_version_id != query.corpus_version_id:
                raise CorpusRejectedError("projection contains mixed corpus membership")
            if record.binding_epoch != query.binding_epoch:
                raise CorpusRejectedError("projection contains mixed binding epoch membership")
            if record.language != query.language:
                continue
            if query.required_curriculum_node_version_ids and record.curriculum_node_version_id not in query.required_curriculum_node_version_ids:
                continue
            matched = tuple(sorted(query_terms & _tokenize(record.retrieval_text)))
            if not matched:
                continue
            tier_weight = {"tier_1": 1.0, "tier_2": 0.85, "tier_3": 0.70}[record.authority_tier]
            score = round((len(matched) / max(len(query_terms), 1)) * record.quality_score * tier_weight, 6)
            hits.append(RetrievalHit(record=record, score=score, matched_terms=matched))
        hits.sort(key=lambda hit: (-hit.score, hit.record.chunk_version_id))
        selected = tuple(hits[: query.top_k])
        snapshot = _sha256_json({
            "activation_key": query.activation_key,
            "corpus_version_id": query.corpus_version_id,
            "binding_epoch": query.binding_epoch,
            "projection_sha256": self.projection.projection_sha256,
            "hit_chunk_version_ids": [hit.record.chunk_version_id for hit in selected],
        })
        return RetrievalResult(query=query, hits=selected, source_snapshot_hash=snapshot)


@dataclass(frozen=True)
class ActivationPlan:
    activation_key: str
    corpus_version_id: str
    previous_corpus_version_id: str | None
    binding_epoch: int
    event_type: str = "activate"
    outbox_events: list[dict[str, Any]] = field(default_factory=list)


class CorpusActivationPlanner:
    @staticmethod
    def plan_activation(
        *,
        activation_key: str,
        corpus_version_id: str,
        previous_corpus_version_id: str | None,
        current_epoch: int,
        event_type: str = "activate",
    ) -> ActivationPlan:
        parse_activation_key(activation_key)
        _require_non_empty(corpus_version_id, "corpus_version_id")
        if event_type not in {"activate", "rollback", "withdraw"}:
            raise CorpusRejectedError("unsupported corpus activation event type")
        next_epoch = current_epoch + 1
        if next_epoch <= 0:
            raise CorpusRejectedError("binding epoch must be positive")
        if event_type == "rollback" and not previous_corpus_version_id:
            raise CorpusRejectedError("rollback requires previous_corpus_version_id")
        return ActivationPlan(
            activation_key=activation_key,
            corpus_version_id=corpus_version_id,
            previous_corpus_version_id=previous_corpus_version_id,
            binding_epoch=next_epoch,
            event_type=event_type,
            outbox_events=[
                {"event_type": "corpus.cache.invalidate", "activation_key": activation_key, "binding_epoch": next_epoch},
                {"event_type": "corpus.metrics.publish", "activation_key": activation_key, "corpus_version_id": corpus_version_id},
                {"event_type": "corpus.audit.publish", "activation_key": activation_key, "activation_action": event_type},
            ],
        )


def versioned_cache_key(*, activation_key: str, corpus_version_id: str, binding_epoch: int) -> str:
    # Compatibility: older Gate 2R.5 dry-runs used compact keys such as
    # "g4-maths:en". New activation and retrieval contracts use the complete
    # five-part key, but cache-key formatting must remain replayable for prior
    # evidence and generic gate verifiers.
    _require_non_empty(activation_key, "activation_key")
    _require_non_empty(corpus_version_id, "corpus_version_id")
    if binding_epoch <= 0:
        raise CorpusRejectedError("binding_epoch must be positive")
    return f"phase02r:corpus:{activation_key}:{corpus_version_id}:epoch:{binding_epoch}"


def canonical_gate2r5_candidates() -> tuple[CorpusChunkCandidate, ...]:
    texts = [
        ("chunk-g4math-numbers-001", "src-caps-g4math-v1", "map-g4math-numbers-001", "node-g4math-numbers-whole-numbers-v1", "Learners compare and order whole numbers and describe place value in Grade 4 Mathematics.", 0.97, 12),
        ("chunk-g4math-fractions-001", "src-caps-g4math-v1", "map-g4math-fractions-001", "node-g4math-fractions-common-v1", "Learners recognise, describe and compare common fractions using diagrams and number lines.", 0.94, 37),
        ("chunk-g4math-measurement-001", "src-caps-g4math-v1", "map-g4math-measurement-001", "node-g4math-measurement-length-v1", "Learners solve practical problems involving length, mass, capacity and time measurement.", 0.91, 83),
    ]
    result = []
    for chunk_id, source_id, mapping_id, node_id, text, quality, page in texts:
        result.append(
            CorpusChunkCandidate(
                chunk_version_id=chunk_id,
                source_version_id=source_id,
                mapping_version_id=mapping_id,
                authority_tier="tier_1",
                rights_status="approved",
                chunk_review_status="approved",
                mapping_review_status="approved",
                quality_score=quality,
                language="en",
                curriculum_node_version_id=node_id,
                source_page_id=f"page-{page}",
                page_start=page,
                page_end=page,
                retrieval_text=text,
                text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                source_sha256="7fec668a6d3b0ed4ae6974a9739970a2128a80553589f682ff5d5bffc02a783e",
                original_object_sha256="7fec668a6d3b0ed4ae6974a9739970a2128a80553589f682ff5d5bffc02a783e",
                language_status="official_source",
            )
        )
    return tuple(result)


def build_gate2r5_fixture_package() -> tuple[CorpusManifest, RetrievalProjection, ActiveCorpusBinding, RetrievalResult]:
    activation_key = build_activation_key(delivery_language="en")
    candidates = canonical_gate2r5_candidates()
    builder = CorpusBuilder()
    manifest = builder.build_manifest(
        corpus_code="CAPS-G4-MATH-EN",
        version_number=1,
        scope={"curriculum_code": "CAPS", "grade": 4, "subject_code": "MATH", "tenant_scope": "global"},
        language="en",
        embedding_model="phase02r-static-policy-embedding",
        embedding_version="gate2r5-no-vector-dry-run-v1",
        activation_key=activation_key,
        candidates=candidates,
    )
    projection = RetrievalProjectionBuilder().build_projection(
        corpus_version_id="corpus-g4math-en-v1",
        activation_key=activation_key,
        binding_epoch=1,
        manifest=manifest,
        candidates=candidates,
    )
    manifest = replace(manifest, retrieval_projection_sha256=projection.projection_sha256)
    binding = ActiveCorpusBinding(
        activation_key=activation_key,
        corpus_version_id="corpus-g4math-en-v1",
        binding_epoch=1,
        manifest_sha256=manifest.manifest_sha256,
    )
    result = ActiveCorpusRetriever(projection, binding).search(
        RetrievalQuery(
            activation_key=activation_key,
            corpus_version_id="corpus-g4math-en-v1",
            binding_epoch=1,
            language="en",
            query_text="compare whole numbers and place value",
            top_k=2,
        )
    )
    return manifest, projection, binding, result
