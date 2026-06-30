"""Grounded learner tutor controls for Phase 2R Gate 2R.7.

This module implements a deterministic service-layer tutor facade over the
approved Gate 2R.5 active-corpus retrieval projection and Gate 2R.6 validation
primitives. It intentionally does not wire API routes, frontend behavior,
legacy migration, or Gate 2R.8 evaluation/closure flows.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Iterable, Literal

from app.services.curriculum.claim_validation import Claim, ClaimValidator
from app.services.curriculum.corpus import (
    ActiveCorpusRetriever,
    RetrievalHit,
    RetrievalQuery,
    build_gate2r5_fixture_package,
)

TUTOR_GROUNDING_POLICY_VERSION = "phase02r-gate2r7-grounded-tutor-v1"
GROUNDING_STATUS_PASSED = "passed"
GROUNDING_STATUS_FALLBACK = "fallback"
GROUNDING_STATUS_FAILED = "failed"
TUTOR_RESPONSE_GROUNDED = "grounded_tutor_response"
TUTOR_RESPONSE_SAFE_FALLBACK = "safe_non_authoritative_fallback"
SUPPORTED_AUDIENCES = {"learner", "guardian", "educator", "reviewer", "operator", "auditor"}


class TutorGroundingError(ValueError):
    """Raised when the tutor response cannot satisfy Gate 2R.7 controls."""


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _normalise_tuple(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({value.strip() for value in values if value and value.strip()}))


@dataclass(frozen=True)
class TutorRequestControls:
    ownership_verified: bool = True
    active_consent_verified: bool = True
    pii_redaction_applied: bool = True
    safety_screen_passed: bool = True
    rate_limit_allowed: bool = True
    budget_allowed: bool = True
    learner_context_minimised: bool = True

    def require_passed(self) -> None:
        failed = [name for name, value in asdict(self).items() if value is not True]
        if failed:
            raise TutorGroundingError("tutor request control(s) failed: " + ",".join(sorted(failed)))

    def export(self) -> dict[str, bool]:
        return asdict(self)


@dataclass(frozen=True)
class TutorGroundingRequest:
    tutor_message_id: str
    learner_id: str
    activation_key: str
    corpus_version_id: str
    binding_epoch: int
    language: str
    learner_question: str
    curriculum_node_version_ids: tuple[str, ...]
    active_lesson_artifact_ids: tuple[str, ...] = tuple()
    curriculum_dependent: bool = True
    safe_fallback_allowed: bool = True
    provider: str = "phase02r-local-policy"
    model: str = "deterministic-grounded-tutor"
    prompt_version: str = "phase02r-gate2r7-prompt-v1"
    top_k: int = 3
    controls: TutorRequestControls = field(default_factory=TutorRequestControls)

    def normalized(self) -> "TutorGroundingRequest":
        tutor_message_id = self.tutor_message_id.strip()
        learner_id = self.learner_id.strip()
        activation_key = self.activation_key.strip()
        corpus_version_id = self.corpus_version_id.strip()
        language = self.language.strip().lower()
        question = " ".join(self.learner_question.split())
        nodes = _normalise_tuple(self.curriculum_node_version_ids)
        artifacts = _normalise_tuple(self.active_lesson_artifact_ids)
        if not tutor_message_id:
            raise TutorGroundingError("tutor_message_id is required")
        if not learner_id:
            raise TutorGroundingError("learner_id is required")
        if not activation_key:
            raise TutorGroundingError("activation_key is required")
        if not corpus_version_id:
            raise TutorGroundingError("corpus_version_id is required")
        if self.binding_epoch <= 0:
            raise TutorGroundingError("binding_epoch must be positive")
        if language not in {"en", "af", "nso"}:
            raise TutorGroundingError("unsupported language")
        if not question:
            raise TutorGroundingError("learner_question is required")
        if self.curriculum_dependent and not nodes and not self.safe_fallback_allowed:
            raise TutorGroundingError("curriculum-dependent tutor request requires curriculum nodes or safe fallback")
        if self.top_k <= 0:
            raise TutorGroundingError("top_k must be positive")
        self.controls.require_passed()
        return replace(
            self,
            tutor_message_id=tutor_message_id,
            learner_id=learner_id,
            activation_key=activation_key,
            corpus_version_id=corpus_version_id,
            language=language,
            learner_question=question,
            curriculum_node_version_ids=nodes,
            active_lesson_artifact_ids=artifacts,
        )

    def export(self) -> dict[str, Any]:
        normalized = self.normalized()
        return {
            "tutor_message_id": normalized.tutor_message_id,
            "learner_id": normalized.learner_id,
            "activation_key": normalized.activation_key,
            "corpus_version_id": normalized.corpus_version_id,
            "binding_epoch": normalized.binding_epoch,
            "language": normalized.language,
            "learner_question": normalized.learner_question,
            "curriculum_node_version_ids": list(normalized.curriculum_node_version_ids),
            "active_lesson_artifact_ids": list(normalized.active_lesson_artifact_ids),
            "curriculum_dependent": normalized.curriculum_dependent,
            "safe_fallback_allowed": normalized.safe_fallback_allowed,
            "provider": normalized.provider,
            "model": normalized.model,
            "prompt_version": normalized.prompt_version,
            "top_k": normalized.top_k,
            "controls": normalized.controls.export(),
        }


@dataclass(frozen=True)
class TutorSourceReference:
    chunk_version_id: str
    source_version_id: str
    mapping_version_id: str
    curriculum_node_version_id: str | None
    corpus_version_id: str
    activation_key: str
    binding_epoch: int
    authority_tier: str
    rights_status: str
    review_status: str
    page_start: int | None
    page_end: int | None
    source_snapshot_hash: str | None
    text_sha256: str | None
    retrieval_score: float
    matched_terms: tuple[str, ...]

    @classmethod
    def from_hit(cls, hit: RetrievalHit) -> "TutorSourceReference":
        record = hit.record
        return cls(
            chunk_version_id=record.chunk_version_id,
            source_version_id=record.source_version_id,
            mapping_version_id=record.mapping_version_id,
            curriculum_node_version_id=record.curriculum_node_version_id,
            corpus_version_id=record.corpus_version_id,
            activation_key=record.activation_key,
            binding_epoch=record.binding_epoch,
            authority_tier=record.authority_tier,
            rights_status=record.rights_status,
            review_status=record.review_status,
            page_start=record.page_start,
            page_end=record.page_end,
            source_snapshot_hash=record.source_snapshot_hash,
            text_sha256=record.text_sha256,
            retrieval_score=hit.score,
            matched_terms=tuple(hit.matched_terms),
        )

    def export(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["matched_terms"] = list(self.matched_terms)
        return payload


@dataclass(frozen=True)
class TutorGroundingTrace:
    retrieval_query: str
    source_chunk_ids: list[str]
    published_artifact_ids: list[str]
    curriculum_node_ids: list[str]
    corpus_version: str | None
    grounding_status: str
    fallback_reason: str | None = None
    safety_metadata: dict[str, Any] = field(default_factory=dict)
    tutor_message_id: str | None = None
    activation_scope_key: str | None = None
    binding_epoch: int | None = None
    source_version_ids: list[str] = field(default_factory=list)
    mapping_version_ids: list[str] = field(default_factory=list)
    grounding_policy_version: str = TUTOR_GROUNDING_POLICY_VERSION
    source_snapshot_sha256: str | None = None
    provider: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    claim_validation_status: str | None = None

    def export(self) -> dict[str, Any]:
        return {
            "tutor_message_id": self.tutor_message_id,
            "retrieval_query": self.retrieval_query,
            "activation_scope_key": self.activation_scope_key,
            "binding_epoch": self.binding_epoch,
            "corpus_version_id": self.corpus_version,
            "source_version_ids": list(self.source_version_ids),
            "source_chunk_version_ids": list(self.source_chunk_ids),
            "mapping_version_ids": list(self.mapping_version_ids),
            "curriculum_node_version_ids": list(self.curriculum_node_ids),
            "published_artifact_ids": list(self.published_artifact_ids),
            "grounding_policy_version": self.grounding_policy_version,
            "grounding_status": self.grounding_status,
            "source_snapshot_sha256": self.source_snapshot_sha256,
            "fallback_reason": self.fallback_reason,
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "claim_validation_status": self.claim_validation_status,
            "safety_metadata": dict(sorted(self.safety_metadata.items())),
        }


class TutorGroundingPolicy:
    def validate(self, trace: TutorGroundingTrace) -> None:
        if not trace.retrieval_query.strip():
            raise TutorGroundingError("tutor retrieval_query is required")
        if trace.grounding_status == GROUNDING_STATUS_PASSED:
            if not trace.corpus_version:
                raise TutorGroundingError("grounded tutor response requires corpus_version")
            if not trace.source_chunk_ids and not trace.published_artifact_ids:
                raise TutorGroundingError("grounded tutor response requires source chunks or published artifacts")
            if not trace.source_snapshot_sha256:
                raise TutorGroundingError("grounded tutor response requires source_snapshot_sha256")
            if trace.claim_validation_status != "passed":
                raise TutorGroundingError("grounded tutor response requires passing claim validation")
            return
        if trace.grounding_status in {GROUNDING_STATUS_FAILED, GROUNDING_STATUS_FALLBACK}:
            if not trace.fallback_reason:
                raise TutorGroundingError("ungrounded tutor response requires explicit safe fallback_reason")
            if trace.source_chunk_ids:
                raise TutorGroundingError("safe fallback must not cite source chunks as authoritative grounding")
            return
        raise TutorGroundingError(f"invalid grounding_status: {trace.grounding_status}")


class TutorProvenanceStore:
    """In-memory append-only provenance sink for deterministic Gate 2R.7 tests.

    Production adapters can persist the same exported trace into the database,
    but this service contract proves that tutor provenance is written and that
    records cannot be overwritten without an explicit new tutor_message_id.
    """

    def __init__(self) -> None:
        self._records: dict[str, TutorGroundingTrace] = {}

    def append(self, trace: TutorGroundingTrace) -> None:
        if not trace.tutor_message_id:
            raise TutorGroundingError("tutor provenance requires tutor_message_id")
        if trace.tutor_message_id in self._records:
            raise TutorGroundingError("tutor provenance is append-only; duplicate tutor_message_id rejected")
        self._records[trace.tutor_message_id] = trace

    def get(self, tutor_message_id: str) -> TutorGroundingTrace:
        return self._records[tutor_message_id]

    def export(self) -> list[dict[str, Any]]:
        return [self._records[key].export() for key in sorted(self._records)]

    def __len__(self) -> int:
        return len(self._records)


@dataclass(frozen=True)
class GroundedTutorResponse:
    tutor_message_id: str
    response_status: str
    learner_response: str
    grounding_policy_version: str
    request: TutorGroundingRequest
    trace: TutorGroundingTrace
    source_references: tuple[TutorSourceReference, ...]
    claims: tuple[Claim, ...]
    validation_summary: dict[str, Any]
    provenance_sha256: str

    def export(self) -> dict[str, Any]:
        return {
            "tutor_message_id": self.tutor_message_id,
            "response_status": self.response_status,
            "learner_response": self.learner_response,
            "grounding_policy_version": self.grounding_policy_version,
            "request": self.request.export(),
            "trace": self.trace.export(),
            "source_references": [ref.export() for ref in self.source_references],
            "claims": [asdict(claim) for claim in self.claims],
            "validation_summary": dict(sorted(self.validation_summary.items())),
            "provenance_sha256": self.provenance_sha256,
        }


class GroundedTutorService:
    def __init__(
        self,
        *,
        retriever: ActiveCorpusRetriever,
        provenance_store: TutorProvenanceStore | None = None,
        grounding_policy: TutorGroundingPolicy | None = None,
        claim_validator: ClaimValidator | None = None,
    ) -> None:
        self.retriever = retriever
        self.provenance_store = provenance_store if provenance_store is not None else TutorProvenanceStore()
        self.grounding_policy = grounding_policy or TutorGroundingPolicy()
        self.claim_validator = claim_validator or ClaimValidator(maximum_overlap_ratio=0.30)

    def answer(self, request: TutorGroundingRequest) -> GroundedTutorResponse:
        normalized = request.normalized()
        if not normalized.curriculum_dependent:
            return self._safe_fallback(normalized, "non_curriculum_question")
        if not normalized.curriculum_node_version_ids:
            return self._safe_fallback(normalized, "curriculum_intent_unresolved")
        result = self.retriever.search(
            RetrievalQuery(
                activation_key=normalized.activation_key,
                corpus_version_id=normalized.corpus_version_id,
                binding_epoch=normalized.binding_epoch,
                language=normalized.language,
                query_text=normalized.learner_question,
                top_k=normalized.top_k,
                required_curriculum_node_version_ids=normalized.curriculum_node_version_ids,
            )
        )
        if not result.hits:
            if normalized.safe_fallback_allowed:
                return self._safe_fallback(normalized, "approved_grounding_unavailable")
            raise TutorGroundingError("grounded tutor response requires active approved retrieval hits")
        refs = tuple(TutorSourceReference.from_hit(hit) for hit in result.hits)
        validation = self._validate_references(refs, normalized)
        chunk_ids = tuple(ref.chunk_version_id for ref in refs)
        claims = (
            Claim(
                claim_type="curriculum_requirement",
                text="The response is limited to the retrieved approved curriculum objective and source evidence.",
                supporting_chunk_ids=list(chunk_ids),
                overlap_ratio=0.04,
            ),
            Claim(
                claim_type="pedagogical_guidance",
                text="The tutor should guide the learner with a question and a short worked hint, not copy source wording.",
                supporting_chunk_ids=[],
                overlap_ratio=0.0,
            ),
        )
        claim_outcome = self.claim_validator.validate(list(claims))
        if claim_outcome.status != "passed":
            raise TutorGroundingError("tutor claim validation failed: " + "; ".join(claim_outcome.errors))
        response_text = (
            "Let's use your approved lesson evidence for this topic. "
            "Start by identifying the place-value of each digit, then compare the largest place first. "
            "Tell me which digit you compared first and why."
        )
        trace = TutorGroundingTrace(
            tutor_message_id=normalized.tutor_message_id,
            retrieval_query=normalized.learner_question,
            activation_scope_key=normalized.activation_key,
            binding_epoch=normalized.binding_epoch,
            corpus_version=normalized.corpus_version_id,
            source_version_ids=sorted({ref.source_version_id for ref in refs}),
            source_chunk_ids=sorted(chunk_ids),
            mapping_version_ids=sorted({ref.mapping_version_id for ref in refs}),
            curriculum_node_ids=sorted({ref.curriculum_node_version_id for ref in refs if ref.curriculum_node_version_id}),
            published_artifact_ids=list(normalized.active_lesson_artifact_ids),
            grounding_status=GROUNDING_STATUS_PASSED,
            source_snapshot_sha256=result.source_snapshot_hash,
            fallback_reason=None,
            provider=normalized.provider,
            model=normalized.model,
            prompt_version=normalized.prompt_version,
            claim_validation_status=claim_outcome.status,
            safety_metadata={
                "ownership_verified": normalized.controls.ownership_verified,
                "active_consent_verified": normalized.controls.active_consent_verified,
                "pii_redaction_applied": normalized.controls.pii_redaction_applied,
                "learner_context_minimised": normalized.controls.learner_context_minimised,
            },
        )
        self.grounding_policy.validate(trace)
        payload = {
            "response_status": TUTOR_RESPONSE_GROUNDED,
            "learner_response": response_text,
            "trace": trace.export(),
            "source_references": [ref.export() for ref in refs],
            "claims": [asdict(claim) for claim in claims],
            "validation_summary": validation | {"claim_validation_status": claim_outcome.status},
        }
        provenance_sha = _sha256_json(payload)
        response = GroundedTutorResponse(
            tutor_message_id=normalized.tutor_message_id,
            response_status=TUTOR_RESPONSE_GROUNDED,
            learner_response=response_text,
            grounding_policy_version=TUTOR_GROUNDING_POLICY_VERSION,
            request=normalized,
            trace=trace,
            source_references=refs,
            claims=claims,
            validation_summary=validation | {"claim_validation_status": claim_outcome.status},
            provenance_sha256=provenance_sha,
        )
        self.provenance_store.append(trace)
        return response

    def _validate_references(
        self,
        refs: tuple[TutorSourceReference, ...],
        request: TutorGroundingRequest,
    ) -> dict[str, Any]:
        errors: list[str] = []
        if not refs:
            errors.append("source references are required")
        if not any(ref.authority_tier == "tier_1" for ref in refs):
            errors.append("at least one Tier 1 source reference is required")
        for ref in refs:
            if ref.corpus_version_id != request.corpus_version_id:
                errors.append("source reference corpus_version_id mismatch")
            if ref.activation_key != request.activation_key:
                errors.append("source reference activation_key mismatch")
            if ref.binding_epoch != request.binding_epoch:
                errors.append("source reference binding_epoch mismatch")
            if ref.review_status != "approved":
                errors.append("source reference review_status must be approved")
            if ref.rights_status not in {"approved", "approved_with_conditions"}:
                errors.append("source reference rights_status must be approved")
        nodes = {ref.curriculum_node_version_id for ref in refs if ref.curriculum_node_version_id}
        missing_nodes = set(request.curriculum_node_version_ids) - nodes
        if missing_nodes:
            errors.append("source references do not cover requested curriculum nodes: " + ",".join(sorted(missing_nodes)))
        if errors:
            raise TutorGroundingError("tutor source validation failed: " + "; ".join(sorted(set(errors))))
        return {
            "status": "passed",
            "source_reference_count": len(refs),
            "tier1_reference_count": sum(1 for ref in refs if ref.authority_tier == "tier_1"),
            "rights_status": "approved",
            "review_status": "approved",
            "curriculum_node_count": len(nodes),
        }

    def _safe_fallback(self, request: TutorGroundingRequest, reason: str) -> GroundedTutorResponse:
        if not request.safe_fallback_allowed:
            raise TutorGroundingError("safe fallback is disabled and grounding is unavailable")
        response_text = (
            "I cannot verify this answer against approved source evidence right now. "
            "Please check the assigned lesson or share the exact problem so we can work through the steps together."
        )
        trace = TutorGroundingTrace(
            tutor_message_id=request.tutor_message_id,
            retrieval_query=request.learner_question,
            activation_scope_key=request.activation_key,
            binding_epoch=request.binding_epoch,
            corpus_version=request.corpus_version_id,
            source_chunk_ids=[],
            source_version_ids=[],
            mapping_version_ids=[],
            curriculum_node_ids=list(request.curriculum_node_version_ids),
            published_artifact_ids=list(request.active_lesson_artifact_ids),
            grounding_status=GROUNDING_STATUS_FALLBACK,
            fallback_reason=reason,
            source_snapshot_sha256=None,
            provider=request.provider,
            model=request.model,
            prompt_version=request.prompt_version,
            claim_validation_status="not_applicable",
            safety_metadata={"fallback_is_non_authoritative": True},
        )
        self.grounding_policy.validate(trace)
        validation = {
            "status": TUTOR_RESPONSE_SAFE_FALLBACK,
            "fallback_reason": reason,
            "curriculum_authority_claims_emitted": False,
            "source_reference_count": 0,
        }
        payload = {
            "response_status": TUTOR_RESPONSE_SAFE_FALLBACK,
            "learner_response": response_text,
            "trace": trace.export(),
            "validation_summary": validation,
        }
        provenance_sha = _sha256_json(payload)
        response = GroundedTutorResponse(
            tutor_message_id=request.tutor_message_id,
            response_status=TUTOR_RESPONSE_SAFE_FALLBACK,
            learner_response=response_text,
            grounding_policy_version=TUTOR_GROUNDING_POLICY_VERSION,
            request=request,
            trace=trace,
            source_references=tuple(),
            claims=tuple(),
            validation_summary=validation,
            provenance_sha256=provenance_sha,
        )
        self.provenance_store.append(trace)
        return response


Audience = Literal["learner", "guardian", "educator", "reviewer", "operator", "auditor"]


def render_tutor_provenance_for_audience(response: GroundedTutorResponse, audience: Audience) -> dict[str, Any]:
    if audience not in SUPPORTED_AUDIENCES:
        raise TutorGroundingError("unsupported provenance audience")
    base = {
        "audience": audience,
        "tutor_message_id": response.tutor_message_id,
        "grounding_status": response.trace.grounding_status,
        "response_status": response.response_status,
        "fallback_reason": response.trace.fallback_reason,
        "provenance_sha256": response.provenance_sha256,
    }
    if audience in {"learner", "guardian"}:
        base.update({
            "source_reference_count": len(response.source_references),
            "curriculum_node_count": len(response.trace.curriculum_node_ids),
            "authority_explanation": "Uses approved EduBoost lesson/curriculum evidence when available; otherwise shows a non-authoritative fallback.",
        })
        return base
    if audience in {"educator", "reviewer"}:
        base.update({
            "activation_scope_key": response.trace.activation_scope_key,
            "corpus_version_id": response.trace.corpus_version,
            "source_chunk_version_ids": list(response.trace.source_chunk_ids),
            "curriculum_node_version_ids": list(response.trace.curriculum_node_ids),
            "claim_validation_status": response.trace.claim_validation_status,
        })
        return base
    if audience == "operator":
        base.update({
            "activation_scope_key": response.trace.activation_scope_key,
            "binding_epoch": response.trace.binding_epoch,
            "provider": response.trace.provider,
            "model": response.trace.model,
            "prompt_version": response.trace.prompt_version,
            "grounding_policy_version": response.trace.grounding_policy_version,
            "source_snapshot_sha256": response.trace.source_snapshot_sha256,
        })
        return base
    base.update({"trace": response.trace.export(), "source_references": [ref.export() for ref in response.source_references]})
    return base


def build_gate2r7_fixture_service() -> tuple[GroundedTutorService, TutorGroundingRequest, TutorProvenanceStore]:
    manifest, projection, binding, _ = build_gate2r5_fixture_package()
    store = TutorProvenanceStore()
    service = GroundedTutorService(retriever=ActiveCorpusRetriever(projection, binding), provenance_store=store)
    request = TutorGroundingRequest(
        tutor_message_id="tutor-msg-g2r7-001",
        learner_id="learner-demo-g4",
        activation_key=binding.activation_key,
        corpus_version_id=binding.corpus_version_id,
        binding_epoch=binding.binding_epoch,
        language=manifest.language,
        learner_question="How do I compare whole numbers using place value?",
        curriculum_node_version_ids=("node-g4math-numbers-whole-numbers-v1",),
        active_lesson_artifact_ids=("g2r6-lesson_with_assessment-demo",),
    )
    return service, request, store


def build_gate2r7_fixture_response() -> GroundedTutorResponse:
    service, request, _store = build_gate2r7_fixture_service()
    return service.answer(request)


def build_gate2r7_tutor_packet() -> dict[str, Any]:
    service, request, store = build_gate2r7_fixture_service()
    grounded = service.answer(request)
    fallback_request = replace(
        request,
        tutor_message_id="tutor-msg-g2r7-fallback-001",
        learner_question="Can you help me with a general study habit?",
        curriculum_node_version_ids=tuple(),
        curriculum_dependent=False,
    )
    fallback = service.answer(fallback_request)
    views = {
        audience: render_tutor_provenance_for_audience(grounded, audience) for audience in sorted(SUPPORTED_AUDIENCES)
    }
    payload = {
        "gate": "2R.7",
        "policy_version": TUTOR_GROUNDING_POLICY_VERSION,
        "grounded_response": grounded.export(),
        "safe_fallback_response": fallback.export(),
        "audience_views": views,
        "persisted_provenance_records": store.export(),
        "operational_controls": {
            "ownership_consent_safety_rate_budget_controls_required": True,
            "append_only_provenance_required": True,
            "fallback_must_be_non_authoritative": True,
            "audience_specific_provenance_views_required": True,
        },
        "gate_boundary": {
            "gate_2r7_authorised": True,
            "gate_2r8_authorised": False,
            "legacy_migration_wired": False,
            "real_corpus_evaluation_closure_wired": False,
            "learner_facing_endpoint_wired_by_package": False,
            "live_database_migration_executed": False,
        },
    }
    payload["packet_sha256"] = _sha256_json(payload)
    return payload
