from __future__ import annotations

from dataclasses import replace

import pytest

from app.services.curriculum.corpus import (
    ActiveCorpusBinding,
    ActiveCorpusRetriever,
    CorpusActivationPlanner,
    CorpusBuilder,
    CorpusRejectedError,
    RetrievalProjectionBuilder,
    RetrievalQuery,
    build_activation_key,
    build_gate2r5_fixture_package,
    canonical_gate2r5_candidates,
    parse_activation_key,
    versioned_cache_key,
)


def test_activation_key_is_complete_and_parseable() -> None:
    key = build_activation_key(curriculum_code="CAPS", grade=4, subject_code="MATH", delivery_language="en", tenant_scope="global")
    assert key == "CAPS:g4:MATH:en:global"
    assert parse_activation_key(key) == {
        "curriculum_code": "CAPS",
        "grade": 4,
        "subject_code": "MATH",
        "delivery_language": "en",
        "tenant_scope": "global",
    }


def test_semantic_corpus_manifest_is_deterministic() -> None:
    candidates = canonical_gate2r5_candidates()
    activation_key = build_activation_key(delivery_language="en")
    builder = CorpusBuilder()
    kwargs = dict(
        corpus_code="CAPS-G4-MATH-EN",
        version_number=1,
        scope={"curriculum_code": "CAPS", "grade": 4, "subject_code": "MATH", "tenant_scope": "global"},
        language="en",
        embedding_model="phase02r-static-policy-embedding",
        embedding_version="gate2r5-no-vector-dry-run-v1",
        activation_key=activation_key,
    )
    first = builder.build_manifest(candidates=candidates, **kwargs)
    second = builder.build_manifest(candidates=tuple(reversed(candidates)), **kwargs)
    assert first.manifest_sha256 == second.manifest_sha256
    assert first.membership_count == 3
    assert first.tier1_membership_count == 3
    assert first.source_snapshot_hash and len(first.source_snapshot_hash) == 64


def test_corpus_rejects_unapproved_or_unsafe_membership() -> None:
    candidate = canonical_gate2r5_candidates()[0]
    builder = CorpusBuilder()
    common = dict(
        corpus_code="CAPS-G4-MATH-EN",
        version_number=1,
        scope={"curriculum_code": "CAPS", "grade": 4, "subject_code": "MATH"},
        language="en",
        embedding_model="test",
        embedding_version="v1",
        activation_key=build_activation_key(delivery_language="en"),
    )
    rejected = [
        replace(candidate, rights_status="rejected"),
        replace(candidate, mapping_review_status="proposed"),
        replace(candidate, chunk_review_status="review_required"),
        replace(candidate, source_status="withdrawn"),
        replace(candidate, language_status="machine_translation_draft"),
        replace(candidate, unresolved_security_warnings=("malware-scan-missing",)),
        replace(candidate, synthetic_fixture=True),
    ]
    for bad in rejected:
        with pytest.raises(CorpusRejectedError):
            builder.build_manifest(candidates=[bad], **common)


def test_corpus_requires_tier1_authority_coverage() -> None:
    candidate = replace(canonical_gate2r5_candidates()[0], authority_tier="tier_2")
    with pytest.raises(CorpusRejectedError, match="Tier 1"):
        CorpusBuilder().build_manifest(
            corpus_code="CAPS-G4-MATH-EN",
            version_number=1,
            scope={"curriculum_code": "CAPS", "grade": 4, "subject_code": "MATH"},
            language="en",
            embedding_model="test",
            embedding_version="v1",
            activation_key=build_activation_key(delivery_language="en"),
            candidates=[candidate],
        )


def test_freeze_requires_manifest_membership_match() -> None:
    candidates = canonical_gate2r5_candidates()
    manifest, _projection, _binding, _retrieval = build_gate2r5_fixture_package()
    frozen = CorpusBuilder().freeze(manifest=manifest, candidates=candidates)
    assert len(frozen.freeze_sha256) == 64
    with pytest.raises(CorpusRejectedError):
        CorpusBuilder().freeze(manifest=manifest, candidates=candidates[:1])


def test_retrieval_projection_is_deterministic_and_manifest_bound() -> None:
    candidates = canonical_gate2r5_candidates()
    manifest, projection, _binding, _retrieval = build_gate2r5_fixture_package()
    projection2 = RetrievalProjectionBuilder().build_projection(
        corpus_version_id=projection.corpus_version_id,
        activation_key=projection.activation_key,
        binding_epoch=projection.binding_epoch,
        manifest=manifest,
        candidates=tuple(reversed(candidates)),
    )
    assert projection.projection_sha256 == projection2.projection_sha256
    with pytest.raises(CorpusRejectedError):
        RetrievalProjectionBuilder().build_projection(
            corpus_version_id=projection.corpus_version_id,
            activation_key=projection.activation_key,
            binding_epoch=projection.binding_epoch,
            manifest=manifest,
            candidates=candidates[:1],
        )


def test_active_corpus_retrieval_rejects_stale_or_mixed_bindings() -> None:
    manifest, projection, binding, retrieval = build_gate2r5_fixture_package()
    assert manifest.manifest_sha256 == binding.manifest_sha256
    assert retrieval.hits
    with pytest.raises(CorpusRejectedError):
        ActiveCorpusRetriever(
            projection,
            ActiveCorpusBinding(
                activation_key=binding.activation_key,
                corpus_version_id="other-corpus",
                binding_epoch=binding.binding_epoch,
                manifest_sha256=binding.manifest_sha256,
            ),
        )
    retriever = ActiveCorpusRetriever(projection, binding)
    with pytest.raises(CorpusRejectedError):
        retriever.search(
            RetrievalQuery(
                activation_key=binding.activation_key,
                corpus_version_id=binding.corpus_version_id,
                binding_epoch=binding.binding_epoch + 1,
                language="en",
                query_text="whole numbers",
            )
        )


def test_retrieval_results_are_real_source_and_objective_filterable() -> None:
    manifest, projection, binding, _ = build_gate2r5_fixture_package()
    result = ActiveCorpusRetriever(projection, binding).search(
        RetrievalQuery(
            activation_key=binding.activation_key,
            corpus_version_id=binding.corpus_version_id,
            binding_epoch=binding.binding_epoch,
            language="en",
            query_text="fractions number lines",
            required_curriculum_node_version_ids=("node-g4math-fractions-common-v1",),
        )
    )
    assert result.hits
    assert all(hit.record.curriculum_node_version_id == "node-g4math-fractions-common-v1" for hit in result.hits)
    assert all(hit.record.source_version_id == "src-caps-g4math-v1" for hit in result.hits)
    assert manifest.source_snapshot_hash == projection.records[0].source_snapshot_hash


def test_activation_and_rollback_plans_increment_epoch_and_emit_outbox() -> None:
    key = build_activation_key(delivery_language="en")
    plan = CorpusActivationPlanner.plan_activation(
        activation_key=key,
        corpus_version_id="corpus-v2",
        previous_corpus_version_id="corpus-v1",
        current_epoch=7,
    )
    assert plan.binding_epoch == 8
    assert {event["event_type"] for event in plan.outbox_events} >= {
        "corpus.cache.invalidate",
        "corpus.metrics.publish",
        "corpus.audit.publish",
    }
    rollback = CorpusActivationPlanner.plan_activation(
        activation_key=key,
        corpus_version_id="corpus-v1",
        previous_corpus_version_id="corpus-v2",
        current_epoch=8,
        event_type="rollback",
    )
    assert rollback.event_type == "rollback"
    assert rollback.binding_epoch == 9


def test_versioned_cache_key_contains_complete_identity() -> None:
    key = build_activation_key(delivery_language="en")
    cache_key = versioned_cache_key(activation_key=key, corpus_version_id="corpus-v1", binding_epoch=4)
    assert key in cache_key
    assert "corpus-v1" in cache_key
    assert "epoch:4" in cache_key
