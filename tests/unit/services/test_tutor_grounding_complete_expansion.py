from dataclasses import replace
import pytest

from app.services.curriculum.tutor_grounding import (
    GROUNDING_STATUS_FAILED,
    GROUNDING_STATUS_FALLBACK,
    GROUNDING_STATUS_PASSED,
    TutorGroundingError,
    TutorGroundingPolicy,
    TutorGroundingRequest,
    TutorGroundingTrace,
    TutorProvenanceStore,
    TutorRequestControls,
    TutorSourceReference,
    build_gate2r7_fixture_service,
    render_tutor_provenance_for_audience,
)


def test_tutor_grounding_request_validation_edges():
    service, base_req, store = build_gate2r7_fixture_service()

    # Empty tutor_message_id
    with pytest.raises(TutorGroundingError, match="tutor_message_id is required"):
        replace(base_req, tutor_message_id="   ").normalized()

    # Empty learner_id
    with pytest.raises(TutorGroundingError, match="learner_id is required"):
        replace(base_req, learner_id="   ").normalized()

    # Empty activation_key
    with pytest.raises(TutorGroundingError, match="activation_key is required"):
        replace(base_req, activation_key="   ").normalized()

    # Empty corpus_version_id
    with pytest.raises(TutorGroundingError, match="corpus_version_id is required"):
        replace(base_req, corpus_version_id="   ").normalized()

    # Non-positive binding_epoch
    with pytest.raises(TutorGroundingError, match="binding_epoch must be positive"):
        replace(base_req, binding_epoch=0).normalized()

    # Unsupported language
    with pytest.raises(TutorGroundingError, match="unsupported language"):
        replace(base_req, language="fr").normalized()

    # Empty learner_question
    with pytest.raises(TutorGroundingError, match="learner_question is required"):
        replace(base_req, learner_question="   ").normalized()

    # Non-positive top_k
    with pytest.raises(TutorGroundingError, match="top_k must be positive"):
        replace(base_req, top_k=0).normalized()

    # Curriculum dependent with no nodes and fallback not allowed
    with pytest.raises(TutorGroundingError, match="requires curriculum nodes or safe fallback"):
        replace(base_req, curriculum_node_version_ids=tuple(), safe_fallback_allowed=False).normalized()

    # Failed control check
    bad_controls = TutorRequestControls(ownership_verified=False)
    with pytest.raises(TutorGroundingError, match="tutor request control.*failed"):
        replace(base_req, controls=bad_controls).normalized()


def test_tutor_grounding_policy_validation_edges():
    policy = TutorGroundingPolicy()

    # Empty retrieval query
    trace_empty_q = TutorGroundingTrace(
        retrieval_query="",
        source_chunk_ids=["chk_1"],
        published_artifact_ids=[],
        curriculum_node_ids=[],
        corpus_version="cv1",
        grounding_status=GROUNDING_STATUS_PASSED,
        source_snapshot_sha256="sha",
        claim_validation_status="passed",
    )
    with pytest.raises(TutorGroundingError, match="retrieval_query is required"):
        policy.validate(trace_empty_q)

    # Passed status without corpus_version
    trace_no_cv = replace(trace_empty_q, retrieval_query="query", corpus_version=None)
    with pytest.raises(TutorGroundingError, match="requires corpus_version"):
        policy.validate(trace_no_cv)

    # Passed status without chunks or artifacts
    trace_no_src = replace(trace_no_cv, corpus_version="cv1", source_chunk_ids=[])
    with pytest.raises(TutorGroundingError, match="requires source chunks or published artifacts"):
        policy.validate(trace_no_src)

    # Passed status without source_snapshot_sha256
    trace_no_snap = replace(trace_no_src, source_chunk_ids=["chk_1"], source_snapshot_sha256=None)
    with pytest.raises(TutorGroundingError, match="requires source_snapshot_sha256"):
        policy.validate(trace_no_snap)

    # Passed status with failing claim validation
    trace_bad_claims = replace(trace_no_snap, source_snapshot_sha256="sha", claim_validation_status="failed")
    with pytest.raises(TutorGroundingError, match="requires passing claim validation"):
        policy.validate(trace_bad_claims)

    # Fallback status without fallback_reason
    trace_no_reason = TutorGroundingTrace(
        retrieval_query="query",
        source_chunk_ids=[],
        published_artifact_ids=[],
        curriculum_node_ids=[],
        corpus_version="cv1",
        grounding_status=GROUNDING_STATUS_FALLBACK,
        fallback_reason=None,
    )
    with pytest.raises(TutorGroundingError, match="requires explicit safe fallback_reason"):
        policy.validate(trace_no_reason)

    # Fallback status citing source chunks
    trace_cite_fallback = replace(trace_no_reason, fallback_reason="reason", source_chunk_ids=["chk_1"])
    with pytest.raises(TutorGroundingError, match="must not cite source chunks"):
        policy.validate(trace_cite_fallback)

    # Invalid status
    trace_invalid_status = replace(trace_cite_fallback, source_chunk_ids=[], grounding_status="unknown_status")
    with pytest.raises(TutorGroundingError, match="invalid grounding_status"):
        policy.validate(trace_invalid_status)


def test_tutor_provenance_store_edges():
    store = TutorProvenanceStore()
    trace = TutorGroundingTrace(
        retrieval_query="query",
        source_chunk_ids=[],
        published_artifact_ids=[],
        curriculum_node_ids=[],
        corpus_version="cv1",
        grounding_status=GROUNDING_STATUS_FALLBACK,
        fallback_reason="test",
        tutor_message_id=None,
    )
    with pytest.raises(TutorGroundingError, match="requires tutor_message_id"):
        store.append(trace)

    valid_trace = replace(trace, tutor_message_id="msg_001")
    store.append(valid_trace)
    assert len(store) == 1
    assert store.get("msg_001") == valid_trace

    # Duplicate append rejection
    with pytest.raises(TutorGroundingError, match="append-only"):
        store.append(valid_trace)


def test_service_reference_validation_errors():
    service, req, _ = build_gate2r7_fixture_service()

    # Empty references
    with pytest.raises(TutorGroundingError, match="source references are required"):
        service._validate_references(tuple(), req)

    valid_ref = TutorSourceReference(
        chunk_version_id="c1",
        source_version_id="s1",
        mapping_version_id="m1",
        curriculum_node_version_id=req.curriculum_node_version_ids[0],
        corpus_version_id=req.corpus_version_id,
        activation_key=req.activation_key,
        binding_epoch=req.binding_epoch,
        authority_tier="tier_2",  # Not tier_1
        rights_status="approved",
        review_status="approved",
        page_start=1,
        page_end=2,
        source_snapshot_hash="hash",
        text_sha256="sha",
        retrieval_score=0.9,
        matched_terms=("term",),
    )

    # Missing Tier 1 reference
    with pytest.raises(TutorGroundingError, match="at least one Tier 1"):
        service._validate_references((valid_ref,), req)

    tier1_ref = replace(valid_ref, authority_tier="tier_1")

    # Mismatched corpus_version_id
    with pytest.raises(TutorGroundingError, match="corpus_version_id mismatch"):
        service._validate_references((replace(tier1_ref, corpus_version_id="wrong"),), req)

    # Mismatched activation_key
    with pytest.raises(TutorGroundingError, match="activation_key mismatch"):
        service._validate_references((replace(tier1_ref, activation_key="wrong"),), req)

    # Mismatched binding_epoch
    with pytest.raises(TutorGroundingError, match="binding_epoch mismatch"):
        service._validate_references((replace(tier1_ref, binding_epoch=999),), req)

    # Review status not approved
    with pytest.raises(TutorGroundingError, match="review_status must be approved"):
        service._validate_references((replace(tier1_ref, review_status="draft"),), req)

    # Rights status not approved
    with pytest.raises(TutorGroundingError, match="rights_status must be approved"):
        service._validate_references((replace(tier1_ref, rights_status="rejected"),), req)

    # Does not cover requested curriculum nodes
    with pytest.raises(TutorGroundingError, match="do not cover requested curriculum nodes"):
        service._validate_references((replace(tier1_ref, curriculum_node_version_id="other_node"),), req)


def test_service_safe_fallback_disabled():
    service, req, _ = build_gate2r7_fixture_service()
    req_no_fallback = replace(req, safe_fallback_allowed=False)
    with pytest.raises(TutorGroundingError, match="safe fallback is disabled"):
        service._safe_fallback(req_no_fallback, "test_reason")


def test_render_provenance_unsupported_audience():
    service, req, _ = build_gate2r7_fixture_service()
    resp = service.answer(req)
    with pytest.raises(TutorGroundingError, match="unsupported provenance audience"):
        render_tutor_provenance_for_audience(resp, "alien_audience")  # type: ignore
