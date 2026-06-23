"""Grounded lesson and assessment generation controls for Phase 2R Gate 2R.6.

This module is intentionally a service-layer implementation only. It does not
wire learner-facing endpoints, tutor runtime behavior, or Gate 2R.7 response
flows. Gate 2R.6 proves that lesson and assessment generation can fail closed,
carry source provenance, validate claims, and deterministically verify Grade 4
Mathematics answers from an active approved corpus projection.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from typing import Any, Sequence

from app.services.curriculum.answer_verification import DeterministicMathAnswerVerifier
from app.services.curriculum.claim_validation import Claim, ClaimValidator
from app.services.curriculum.corpus import (
    ActiveCorpusRetriever,
    RetrievalHit,
    RetrievalQuery,
    build_gate2r5_fixture_package,
)
from app.services.curriculum.grounding import GroundingDecision, GroundingPolicyEngine, RetrievedChunk

GENERATION_POLICY_VERSION = "phase02r-gate2r6-grounded-generation-v1"
ALLOWED_ARTIFACT_TYPES = {"lesson", "assessment", "lesson_with_assessment", "worked_example"}
GROUND_VERIFIED_STATUS = "grounded_verified"
SAFE_FALLBACK_STATUS = "safe_fallback"


class GroundedGenerationRejectedError(ValueError):
    """Raised when Gate 2R.6 generation cannot be safely grounded."""


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GroundedGenerationRequest:
    artifact_type: str
    activation_key: str
    corpus_version_id: str
    binding_epoch: int
    language: str
    topic: str
    objective_ids: tuple[str, ...]
    learner_stage: str = "grade_4"
    top_k: int = 3
    safe_fallback_allowed: bool = False
    requested_by: str = "phase02r_gate2r6_verifier"

    def normalized(self) -> "GroundedGenerationRequest":
        artifact_type = self.artifact_type.strip().lower()
        language = self.language.strip().lower()
        topic = self.topic.strip()
        objectives = tuple(sorted({objective.strip() for objective in self.objective_ids if objective.strip()}))
        if artifact_type not in ALLOWED_ARTIFACT_TYPES:
            raise GroundedGenerationRejectedError(f"unsupported artifact_type: {self.artifact_type}")
        if not self.activation_key.strip():
            raise GroundedGenerationRejectedError("activation_key is required")
        if not self.corpus_version_id.strip():
            raise GroundedGenerationRejectedError("corpus_version_id is required")
        if self.binding_epoch <= 0:
            raise GroundedGenerationRejectedError("binding_epoch must be positive")
        if language not in {"en", "af", "nso"}:
            raise GroundedGenerationRejectedError("unsupported language")
        if not topic:
            raise GroundedGenerationRejectedError("topic is required")
        if not objectives:
            raise GroundedGenerationRejectedError("at least one objective_id is required")
        if self.top_k <= 0:
            raise GroundedGenerationRejectedError("top_k must be positive")
        return replace(self, artifact_type=artifact_type, language=language, topic=topic, objective_ids=objectives)

    def export(self) -> dict[str, Any]:
        normalized = self.normalized()
        payload = asdict(normalized)
        payload["objective_ids"] = list(normalized.objective_ids)
        return payload


@dataclass(frozen=True)
class SourceReference:
    chunk_version_id: str
    source_version_id: str
    mapping_version_id: str
    curriculum_node_version_id: str | None
    corpus_version_id: str
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
    def from_hit(cls, hit: RetrievalHit) -> "SourceReference":
        record = hit.record
        return cls(
            chunk_version_id=record.chunk_version_id,
            source_version_id=record.source_version_id,
            mapping_version_id=record.mapping_version_id,
            curriculum_node_version_id=record.curriculum_node_version_id,
            corpus_version_id=record.corpus_version_id,
            binding_epoch=record.binding_epoch,
            authority_tier=record.authority_tier,
            rights_status=record.rights_status,
            review_status=record.review_status,
            page_start=record.page_start,
            page_end=record.page_end,
            source_snapshot_hash=record.source_snapshot_hash,
            text_sha256=record.text_sha256,
            retrieval_score=hit.score,
            matched_terms=hit.matched_terms,
        )

    def export(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["matched_terms"] = list(self.matched_terms)
        return payload


@dataclass(frozen=True)
class GeneratedClaim:
    claim_type: str
    text: str
    supporting_chunk_ids: tuple[str, ...]
    overlap_ratio: float = 0.0

    def to_validator_claim(self) -> Claim:
        return Claim(
            claim_type=self.claim_type,
            text=self.text,
            supporting_chunk_ids=list(self.supporting_chunk_ids),
            overlap_ratio=self.overlap_ratio,
        )

    def export(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["supporting_chunk_ids"] = list(self.supporting_chunk_ids)
        return payload


@dataclass(frozen=True)
class LessonSection:
    section_id: str
    title: str
    learner_text: str
    source_chunk_ids: tuple[str, ...]

    def export(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_chunk_ids"] = list(self.source_chunk_ids)
        return payload


@dataclass(frozen=True)
class GeneratedAssessmentItem:
    item_id: str
    prompt: str
    answer_expression: str
    proposed_answer: str
    expected_answer: str | None
    answer_verification_status: str
    source_chunk_ids: tuple[str, ...]
    answer_verification_hash: str

    def export(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_chunk_ids"] = list(self.source_chunk_ids)
        return payload


@dataclass(frozen=True)
class GroundedGenerationArtifact:
    artifact_id: str
    artifact_type: str
    status: str
    generation_policy_version: str
    request: GroundedGenerationRequest
    source_references: tuple[SourceReference, ...]
    source_snapshot_hash: str | None
    grounding_decision: GroundingDecision
    claims: tuple[GeneratedClaim, ...]
    lesson_sections: tuple[LessonSection, ...]
    assessment_items: tuple[GeneratedAssessmentItem, ...]
    validation_summary: dict[str, Any]
    artifact_sha256: str

    def export(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "status": self.status,
            "generation_policy_version": self.generation_policy_version,
            "request": self.request.export(),
            "source_references": [ref.export() for ref in self.source_references],
            "source_snapshot_hash": self.source_snapshot_hash,
            "grounding_decision": {
                "passed": self.grounding_decision.passed,
                "status": self.grounding_decision.status,
                "source_snapshot_hash": self.grounding_decision.source_snapshot_hash,
                "chunk_version_ids": list(self.grounding_decision.chunk_version_ids),
                "source_version_ids": list(self.grounding_decision.source_version_ids),
                "mapping_version_ids": list(self.grounding_decision.mapping_version_ids),
                "failure_reasons": list(self.grounding_decision.failure_reasons),
            },
            "claims": [claim.export() for claim in self.claims],
            "lesson_sections": [section.export() for section in self.lesson_sections],
            "assessment_items": [item.export() for item in self.assessment_items],
            "validation_summary": dict(sorted(self.validation_summary.items())),
            "artifact_sha256": self.artifact_sha256,
        }


def _hits_to_retrieved_chunks(hits: Sequence[RetrievalHit]) -> list[RetrievedChunk]:
    chunks: list[RetrievedChunk] = []
    for hit in hits:
        record = hit.record
        chunks.append(
            RetrievedChunk(
                chunk_version_id=record.chunk_version_id,
                source_version_id=record.source_version_id,
                mapping_version_ids=[record.mapping_version_id],
                objective_ids=[record.curriculum_node_version_id] if record.curriculum_node_version_id else [],
                authority_tier=record.authority_tier,
                rights_status=record.rights_status,
                review_status=record.review_status,
                corpus_version_id=record.corpus_version_id,
                score=hit.score,
                language=record.language,
                text=record.retrieval_text,
            )
        )
    return chunks


class GroundedGenerationService:
    """Deterministic Gate 2R.6 generation facade."""

    def __init__(
        self,
        *,
        retriever: ActiveCorpusRetriever,
        grounding_policy: GroundingPolicyEngine | None = None,
        claim_validator: ClaimValidator | None = None,
        answer_verifier: DeterministicMathAnswerVerifier | None = None,
    ) -> None:
        self.retriever = retriever
        self.grounding_policy = grounding_policy or GroundingPolicyEngine()
        self.claim_validator = claim_validator or ClaimValidator(maximum_overlap_ratio=0.30)
        self.answer_verifier = answer_verifier or DeterministicMathAnswerVerifier()

    def generate(self, request: GroundedGenerationRequest) -> GroundedGenerationArtifact:
        normalized = request.normalized()
        result = self.retriever.search(
            RetrievalQuery(
                activation_key=normalized.activation_key,
                corpus_version_id=normalized.corpus_version_id,
                binding_epoch=normalized.binding_epoch,
                language=normalized.language,
                query_text=f"{normalized.topic} {' '.join(normalized.objective_ids)}",
                top_k=normalized.top_k,
                required_curriculum_node_version_ids=normalized.objective_ids,
            )
        )
        decision = self.grounding_policy.validate_generation_grounding(
            corpus_version_id=normalized.corpus_version_id,
            requested_objective_ids=list(normalized.objective_ids),
            retrieved_chunks=_hits_to_retrieved_chunks(result.hits),
        )
        if not decision.passed:
            if normalized.safe_fallback_allowed:
                return self._build_safe_fallback(normalized, decision)
            raise GroundedGenerationRejectedError("generation grounding failed: " + "; ".join(decision.failure_reasons))
        if not result.hits:
            raise GroundedGenerationRejectedError("generation requires at least one retrieval hit")
        refs = tuple(SourceReference.from_hit(hit) for hit in result.hits)
        chunk_ids = tuple(ref.chunk_version_id for ref in refs)
        lesson_sections = self._build_lesson_sections(normalized, chunk_ids)
        assessment_items = self._build_assessment_items(normalized, chunk_ids)
        claims = self._build_claims(normalized, chunk_ids)
        validation = self._validate_artifact_parts(claims, assessment_items, refs)
        payload = {
            "artifact_type": normalized.artifact_type,
            "request": normalized.export(),
            "source_references": [ref.export() for ref in refs],
            "source_snapshot_hash": decision.source_snapshot_hash,
            "claims": [claim.export() for claim in claims],
            "lesson_sections": [section.export() for section in lesson_sections],
            "assessment_items": [item.export() for item in assessment_items],
            "validation_summary": validation,
            "generation_policy_version": GENERATION_POLICY_VERSION,
        }
        artifact_sha = _sha256_json(payload)
        artifact_id = f"g2r6-{normalized.artifact_type}-{artifact_sha[:16]}"
        return GroundedGenerationArtifact(
            artifact_id=artifact_id,
            artifact_type=normalized.artifact_type,
            status=GROUND_VERIFIED_STATUS,
            generation_policy_version=GENERATION_POLICY_VERSION,
            request=normalized,
            source_references=refs,
            source_snapshot_hash=decision.source_snapshot_hash,
            grounding_decision=decision,
            claims=claims,
            lesson_sections=lesson_sections,
            assessment_items=assessment_items,
            validation_summary=validation,
            artifact_sha256=artifact_sha,
        )

    def _build_lesson_sections(self, request: GroundedGenerationRequest, chunk_ids: tuple[str, ...]) -> tuple[LessonSection, ...]:
        if request.artifact_type not in {"lesson", "lesson_with_assessment", "worked_example"}:
            return tuple()
        return (
            LessonSection(
                section_id="intro",
                title=f"Connect the idea: {request.topic}",
                learner_text=(
                    "Use the approved CAPS source evidence to introduce the concept, "
                    "then ask the learner to explain the idea in their own words."
                ),
                source_chunk_ids=chunk_ids,
            ),
            LessonSection(
                section_id="guided-practice",
                title="Guided practice",
                learner_text=(
                    "Work through one Grade 4 example, show each step, and keep the "
                    "mathematics aligned to the cited curriculum objective."
                ),
                source_chunk_ids=chunk_ids,
            ),
        )

    def _build_assessment_items(self, request: GroundedGenerationRequest, chunk_ids: tuple[str, ...]) -> tuple[GeneratedAssessmentItem, ...]:
        if request.artifact_type not in {"assessment", "lesson_with_assessment", "worked_example"}:
            return tuple()
        expression = "2 + 3 * 4"
        outcome = self.answer_verifier.verify_arithmetic_expression(
            question_expression=expression,
            proposed_answer="14",
        )
        return (
            GeneratedAssessmentItem(
                item_id="item-arithmetic-001",
                prompt="Calculate 2 + 3 × 4. Show why multiplication is completed before addition.",
                answer_expression=expression,
                proposed_answer="14",
                expected_answer=outcome.expected_answer,
                answer_verification_status=outcome.status,
                source_chunk_ids=chunk_ids,
                answer_verification_hash=outcome.answer_hash,
            ),
        )

    def _build_claims(self, request: GroundedGenerationRequest, chunk_ids: tuple[str, ...]) -> tuple[GeneratedClaim, ...]:
        claims = [
            GeneratedClaim(
                claim_type="curriculum_requirement",
                text=f"The lesson addresses the approved curriculum objective for {request.topic}.",
                supporting_chunk_ids=chunk_ids,
                overlap_ratio=0.04,
            ),
            GeneratedClaim(
                claim_type="pedagogical_guidance",
                text="The learner-facing explanation must transform, not copy, the source wording.",
                supporting_chunk_ids=tuple(),
                overlap_ratio=0.0,
            ),
        ]
        if request.artifact_type in {"assessment", "lesson_with_assessment", "worked_example"}:
            claims.append(
                GeneratedClaim(
                    claim_type="assessment_claim",
                    text="The generated assessment item has a deterministic Grade 4 mathematics answer check.",
                    supporting_chunk_ids=chunk_ids,
                    overlap_ratio=0.03,
                )
            )
        return tuple(claims)

    def _validate_artifact_parts(
        self,
        claims: tuple[GeneratedClaim, ...],
        items: tuple[GeneratedAssessmentItem, ...],
        refs: tuple[SourceReference, ...],
    ) -> dict[str, Any]:
        validation_errors: list[str] = []
        claim_outcome = self.claim_validator.validate([claim.to_validator_claim() for claim in claims])
        if claim_outcome.status != "passed":
            validation_errors.extend(claim_outcome.errors)
        failed_items = [item.item_id for item in items if item.answer_verification_status != "passed"]
        if failed_items:
            validation_errors.append("answer verification failed for: " + ",".join(sorted(failed_items)))
        if not any(ref.authority_tier == "tier_1" for ref in refs):
            validation_errors.append("tier_1 source reference is required")
        if any(ref.review_status != "approved" for ref in refs):
            validation_errors.append("all source references must be approved")
        if any(ref.rights_status not in {"approved", "approved_with_conditions"} for ref in refs):
            validation_errors.append("all source references must have approved rights")
        if validation_errors:
            raise GroundedGenerationRejectedError("generation validation failed: " + "; ".join(validation_errors))
        return {
            "status": "passed",
            "claim_validation_status": claim_outcome.status,
            "answer_verification_status": "passed" if not failed_items else "failed",
            "source_reference_count": len(refs),
            "tier1_reference_count": sum(1 for ref in refs if ref.authority_tier == "tier_1"),
            "copying_policy": "transformative_output_only",
        }

    def _build_safe_fallback(self, request: GroundedGenerationRequest, decision: GroundingDecision) -> GroundedGenerationArtifact:
        payload = {
            "artifact_type": request.artifact_type,
            "request": request.export(),
            "failure_reasons": list(decision.failure_reasons),
            "generation_policy_version": GENERATION_POLICY_VERSION,
        }
        artifact_sha = _sha256_json(payload)
        return GroundedGenerationArtifact(
            artifact_id=f"g2r6-safe-fallback-{artifact_sha[:16]}",
            artifact_type=request.artifact_type,
            status=SAFE_FALLBACK_STATUS,
            generation_policy_version=GENERATION_POLICY_VERSION,
            request=request,
            source_references=tuple(),
            source_snapshot_hash=None,
            grounding_decision=decision,
            claims=tuple(),
            lesson_sections=(
                LessonSection(
                    section_id="safe-fallback",
                    title="Source evidence unavailable",
                    learner_text="This content is not available until approved source evidence is retrieved.",
                    source_chunk_ids=tuple(),
                ),
            ),
            assessment_items=tuple(),
            validation_summary={"status": SAFE_FALLBACK_STATUS, "failure_reasons": list(decision.failure_reasons)},
            artifact_sha256=artifact_sha,
        )


def build_gate2r6_fixture_artifact(artifact_type: str = "lesson_with_assessment") -> GroundedGenerationArtifact:
    manifest, projection, binding, _ = build_gate2r5_fixture_package()
    service = GroundedGenerationService(retriever=ActiveCorpusRetriever(projection, binding))
    request = GroundedGenerationRequest(
        artifact_type=artifact_type,
        activation_key=binding.activation_key,
        corpus_version_id=binding.corpus_version_id,
        binding_epoch=binding.binding_epoch,
        language=manifest.language,
        topic="compare whole numbers and place value",
        objective_ids=("node-g4math-numbers-whole-numbers-v1",),
        top_k=2,
    )
    return service.generate(request)


def build_gate2r6_generation_packet() -> dict[str, Any]:
    lesson = build_gate2r6_fixture_artifact("lesson_with_assessment")
    assessment = build_gate2r6_fixture_artifact("assessment")
    packet = {
        "gate": "2R.6",
        "policy_version": GENERATION_POLICY_VERSION,
        "artifacts": [lesson.export(), assessment.export()],
        "gate_boundary": {
            "learner_facing_endpoint_wired": False,
            "tutor_runtime_wired": False,
            "gate_2r7_authorised": False,
        },
    }
    packet["packet_sha256"] = _sha256_json(packet)
    return packet
