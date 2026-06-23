from __future__ import annotations

from dataclasses import replace

import pytest

from app.services.curriculum.answer_verification import DeterministicMathAnswerVerifier
from app.services.curriculum.claim_validation import Claim, ClaimValidator
from app.services.curriculum.corpus import ActiveCorpusRetriever, build_gate2r5_fixture_package
from app.services.curriculum.generation import (
    GENERATION_POLICY_VERSION,
    GROUND_VERIFIED_STATUS,
    GroundedGenerationRejectedError,
    GroundedGenerationRequest,
    GroundedGenerationService,
    build_gate2r6_fixture_artifact,
    build_gate2r6_generation_packet,
)


def _service_and_request() -> tuple[GroundedGenerationService, GroundedGenerationRequest]:
    manifest, projection, binding, _ = build_gate2r5_fixture_package()
    service = GroundedGenerationService(retriever=ActiveCorpusRetriever(projection, binding))
    request = GroundedGenerationRequest(
        artifact_type="lesson_with_assessment",
        activation_key=binding.activation_key,
        corpus_version_id=binding.corpus_version_id,
        binding_epoch=binding.binding_epoch,
        language=manifest.language,
        topic="compare whole numbers and place value",
        objective_ids=("node-g4math-numbers-whole-numbers-v1",),
        top_k=2,
    )
    return service, request


def test_grounded_lesson_with_assessment_is_generated_with_provenance() -> None:
    artifact = build_gate2r6_fixture_artifact("lesson_with_assessment")
    assert artifact.status == GROUND_VERIFIED_STATUS
    assert artifact.generation_policy_version == GENERATION_POLICY_VERSION
    assert artifact.source_references
    assert artifact.source_snapshot_hash and len(artifact.source_snapshot_hash) == 64
    assert artifact.lesson_sections
    assert artifact.assessment_items
    assert artifact.validation_summary["status"] == "passed"


def test_generated_artifact_is_deterministic() -> None:
    first = build_gate2r6_fixture_artifact("lesson_with_assessment")
    second = build_gate2r6_fixture_artifact("lesson_with_assessment")
    assert first.artifact_sha256 == second.artifact_sha256
    assert first.artifact_id == second.artifact_id


def test_generation_packet_is_deterministic_and_blocks_gate2r7_wiring() -> None:
    first = build_gate2r6_generation_packet()
    second = build_gate2r6_generation_packet()
    assert first["packet_sha256"] == second["packet_sha256"]
    assert first["gate_boundary"]["tutor_runtime_wired"] is False
    assert first["gate_boundary"]["learner_facing_endpoint_wired"] is False
    assert first["gate_boundary"]["gate_2r7_authorised"] is False


def test_generation_fails_closed_for_unknown_objective() -> None:
    service, request = _service_and_request()
    with pytest.raises(GroundedGenerationRejectedError):
        service.generate(replace(request, objective_ids=("node-does-not-exist",)))


def test_explicit_safe_fallback_does_not_emit_grounded_assessment() -> None:
    service, request = _service_and_request()
    artifact = service.generate(replace(request, objective_ids=("node-does-not-exist",), safe_fallback_allowed=True))
    assert artifact.status == "safe_fallback"
    assert artifact.assessment_items == tuple()
    assert artifact.source_references == tuple()


def test_assessment_item_answer_is_deterministically_verified() -> None:
    artifact = build_gate2r6_fixture_artifact("assessment")
    assert artifact.assessment_items
    assert all(item.answer_verification_status == "passed" for item in artifact.assessment_items)
    assert DeterministicMathAnswerVerifier().verify_arithmetic_expression(
        question_expression="2 + 3 * 4", proposed_answer="13"
    ).status == "failed"


def test_curriculum_claim_requires_supporting_source_chunks() -> None:
    outcome = ClaimValidator().validate([Claim("curriculum_requirement", "CAPS requires unsupported content", [])])
    assert outcome.status == "failed"
    assert any("requires supporting source chunks" in error for error in outcome.errors)


def test_enrichment_claim_cannot_be_promoted_to_caps_requirement() -> None:
    outcome = ClaimValidator().validate([
        Claim("enrichment", "CAPS requires this enrichment activity", [], 0.0)
    ])
    assert outcome.status == "failed"


def test_assessment_only_artifact_has_no_lesson_sections() -> None:
    artifact = build_gate2r6_fixture_artifact("assessment")
    assert artifact.assessment_items
    assert artifact.lesson_sections == tuple()


def test_lesson_only_artifact_has_no_assessment_items() -> None:
    artifact = build_gate2r6_fixture_artifact("lesson")
    assert artifact.lesson_sections
    assert artifact.assessment_items == tuple()


def test_generation_rejects_invalid_request_without_source_access() -> None:
    service, request = _service_and_request()
    with pytest.raises(GroundedGenerationRejectedError):
        service.generate(replace(request, artifact_type="tutor_response"))
