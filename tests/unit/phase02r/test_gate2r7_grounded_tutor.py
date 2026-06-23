from __future__ import annotations

from dataclasses import replace

import pytest

from app.services.curriculum.tutor_grounding import (
    GROUNDING_STATUS_FALLBACK,
    GROUNDING_STATUS_PASSED,
    TUTOR_GROUNDING_POLICY_VERSION,
    TUTOR_RESPONSE_GROUNDED,
    TUTOR_RESPONSE_SAFE_FALLBACK,
    TutorGroundingError,
    TutorGroundingPolicy,
    TutorGroundingTrace,
    TutorRequestControls,
    build_gate2r7_fixture_response,
    build_gate2r7_fixture_service,
    build_gate2r7_tutor_packet,
    render_tutor_provenance_for_audience,
)


def test_grounded_tutor_response_uses_active_corpus_and_persists_provenance() -> None:
    service, request, store = build_gate2r7_fixture_service()
    response = service.answer(request)
    assert response.response_status == TUTOR_RESPONSE_GROUNDED
    assert response.grounding_policy_version == TUTOR_GROUNDING_POLICY_VERSION
    assert response.trace.grounding_status == GROUNDING_STATUS_PASSED
    assert response.trace.source_chunk_ids
    assert response.trace.source_snapshot_sha256 and len(response.trace.source_snapshot_sha256) == 64
    assert len(store) == 1
    assert store.get(response.tutor_message_id).source_chunk_ids == response.trace.source_chunk_ids


def test_tutor_response_is_deterministic() -> None:
    first = build_gate2r7_fixture_response()
    second = build_gate2r7_fixture_response()
    assert first.provenance_sha256 == second.provenance_sha256
    assert first.trace.export() == second.trace.export()


def test_tutor_packet_is_deterministic_and_blocks_gate2r8() -> None:
    first = build_gate2r7_tutor_packet()
    second = build_gate2r7_tutor_packet()
    assert first["packet_sha256"] == second["packet_sha256"]
    assert first["gate_boundary"]["gate_2r7_authorised"] is True
    assert first["gate_boundary"]["gate_2r8_authorised"] is False
    assert first["gate_boundary"]["legacy_migration_wired"] is False
    assert first["gate_boundary"]["real_corpus_evaluation_closure_wired"] is False


def test_safe_fallback_is_non_authoritative_when_grounding_missing() -> None:
    service, request, store = build_gate2r7_fixture_service()
    fallback = service.answer(
        replace(
            request,
            tutor_message_id="tutor-msg-safe-fallback-test",
            curriculum_node_version_ids=("node-does-not-exist",),
            learner_question="Tell me the CAPS rule for an unsupported topic",
            safe_fallback_allowed=True,
        )
    )
    assert fallback.response_status == TUTOR_RESPONSE_SAFE_FALLBACK
    assert fallback.trace.grounding_status == GROUNDING_STATUS_FALLBACK
    assert fallback.trace.fallback_reason == "approved_grounding_unavailable"
    assert fallback.source_references == tuple()
    assert fallback.trace.source_chunk_ids == []
    assert "CAPS requires" not in fallback.learner_response
    assert len(store) == 1


def test_missing_grounding_without_fallback_fails_closed() -> None:
    service, request, _store = build_gate2r7_fixture_service()
    with pytest.raises(TutorGroundingError):
        service.answer(
            replace(
                request,
                curriculum_node_version_ids=("node-does-not-exist",),
                safe_fallback_allowed=False,
            )
        )


def test_failed_consent_or_safety_controls_block_tutor_response() -> None:
    service, request, _store = build_gate2r7_fixture_service()
    with pytest.raises(TutorGroundingError, match="active_consent_verified"):
        service.answer(replace(request, controls=TutorRequestControls(active_consent_verified=False)))
    with pytest.raises(TutorGroundingError, match="safety_screen_passed"):
        service.answer(
            replace(
                request,
                tutor_message_id="tutor-msg-failed-safety",
                controls=TutorRequestControls(safety_screen_passed=False),
            )
        )


def test_append_only_provenance_rejects_duplicate_message_id() -> None:
    service, request, _store = build_gate2r7_fixture_service()
    service.answer(request)
    with pytest.raises(TutorGroundingError, match="append-only"):
        service.answer(request)


def test_audience_specific_provenance_views_are_access_shaped() -> None:
    response = build_gate2r7_fixture_response()
    learner = render_tutor_provenance_for_audience(response, "learner")
    educator = render_tutor_provenance_for_audience(response, "educator")
    operator = render_tutor_provenance_for_audience(response, "operator")
    auditor = render_tutor_provenance_for_audience(response, "auditor")
    assert "source_chunk_version_ids" not in learner
    assert learner["source_reference_count"] == len(response.source_references)
    assert educator["source_chunk_version_ids"] == response.trace.source_chunk_ids
    assert operator["source_snapshot_sha256"] == response.trace.source_snapshot_sha256
    assert auditor["source_references"]


def test_unsupported_provenance_audience_is_rejected() -> None:
    with pytest.raises(TutorGroundingError):
        render_tutor_provenance_for_audience(build_gate2r7_fixture_response(), "public")  # type: ignore[arg-type]


def test_grounding_policy_requires_snapshot_and_claim_validation_for_grounded_trace() -> None:
    trace = TutorGroundingTrace(
        retrieval_query="place value",
        source_chunk_ids=["chunk-1"],
        published_artifact_ids=[],
        curriculum_node_ids=["node-1"],
        corpus_version="corpus-1",
        grounding_status=GROUNDING_STATUS_PASSED,
        source_snapshot_sha256=None,
        claim_validation_status="passed",
    )
    with pytest.raises(TutorGroundingError, match="source_snapshot"):
        TutorGroundingPolicy().validate(trace)


def test_fallback_policy_requires_explicit_reason() -> None:
    trace = TutorGroundingTrace(
        retrieval_query="place value",
        source_chunk_ids=[],
        published_artifact_ids=[],
        curriculum_node_ids=[],
        corpus_version="corpus-1",
        grounding_status=GROUNDING_STATUS_FALLBACK,
        fallback_reason=None,
    )
    with pytest.raises(TutorGroundingError, match="fallback_reason"):
        TutorGroundingPolicy().validate(trace)


def test_validation_summary_records_required_controls() -> None:
    response = build_gate2r7_fixture_response()
    assert response.validation_summary["status"] == "passed"
    assert response.validation_summary["claim_validation_status"] == "passed"
    assert response.validation_summary["tier1_reference_count"] >= 1
    assert response.validation_summary["rights_status"] == "approved"
