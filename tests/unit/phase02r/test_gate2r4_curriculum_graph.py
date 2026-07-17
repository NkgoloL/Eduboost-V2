from __future__ import annotations

import copy

import pytest

from app.services.curriculum.graph import (
    CHUNK_NUMBERS_ID,
    MAPPING_NUMBERS_VERSION_ID,
    NODE_NUMBERS_VERSION_ID,
    Gate2R4ValidationError,
    LanguageAuthorityStatus,
    SourceCurriculumMappingVersion,
    SupportType,
    build_gate2r4_reference_graph,
    export_gate2r4_reference_graph,
    validate_gate2r4_reference_graph,
)


def test_curriculum_node_versions_are_immutable() -> None:
    graph = build_gate2r4_reference_graph()
    node = graph.node_versions[NODE_NUMBERS_VERSION_ID]
    assert node.status == "approved"
    with pytest.raises(Gate2R4ValidationError, match="immutable"):
        node.with_changes(topic="Changed topic")


def test_curriculum_mapping_requires_existing_source_chunk() -> None:
    graph = build_gate2r4_reference_graph()
    mapping = SourceCurriculumMappingVersion(
        mapping_id="mapping-missing-source",
        mapping_version_id="mappingver-missing-source-v1",
        source_chunk_version_id="missing-chunk",
        curriculum_node_version_id=NODE_NUMBERS_VERSION_ID,
        support_type=SupportType.DIRECT_SUPPORT.value,
        authority_tier="tier_1",
        language="en",
        mapping_rationale="Bad source reference must be rejected.",
        proposed_by="mapper",
        proposed_at="2026-06-22T00:00:00+00:00",
    )
    with pytest.raises(Gate2R4ValidationError, match="unknown source chunk"):
        graph.add_mapping_version(mapping)


def test_curriculum_mapping_requires_existing_curriculum_node() -> None:
    graph = build_gate2r4_reference_graph()
    graph.add_source_chunk("chunk-extra")
    mapping = SourceCurriculumMappingVersion(
        mapping_id="mapping-missing-node",
        mapping_version_id="mappingver-missing-node-v1",
        source_chunk_version_id="chunk-extra",
        curriculum_node_version_id="missing-node-version",
        support_type=SupportType.DIRECT_SUPPORT.value,
        authority_tier="tier_1",
        language="en",
        mapping_rationale="Bad node reference must be rejected.",
        proposed_by="mapper",
        proposed_at="2026-06-22T00:00:00+00:00",
    )
    with pytest.raises(Gate2R4ValidationError, match="unknown curriculum node"):
        graph.add_mapping_version(mapping)


def test_only_approved_mapping_is_corpus_eligible() -> None:
    graph = build_gate2r4_reference_graph()
    approved = graph.mapping_versions[MAPPING_NUMBERS_VERSION_ID]
    proposed = SourceCurriculumMappingVersion(
        mapping_id="mapping-proposed",
        mapping_version_id="mappingver-proposed-v1",
        source_chunk_version_id=CHUNK_NUMBERS_ID,
        curriculum_node_version_id=NODE_NUMBERS_VERSION_ID,
        support_type=SupportType.DIRECT_SUPPORT.value,
        authority_tier="tier_1",
        language="en",
        mapping_rationale="Proposal only.",
        proposed_by="mapper",
        proposed_at="2026-06-22T00:00:00+00:00",
    )
    assert approved.corpus_eligible is True
    assert proposed.corpus_eligible is False


def test_tier1_support_required_for_caps_requirement() -> None:
    graph = build_gate2r4_reference_graph()
    assert graph.validate_tier1_support() == []
    broken = copy.deepcopy(graph)
    broken.mapping_versions = {}
    assert "lacks approved Tier 1 support" in broken.validate_tier1_support()[0]


def test_mapping_review_is_append_only() -> None:
    graph = build_gate2r4_reference_graph()
    report = graph.validation_report()
    assert report["mapping_review_validation"]["valid"] is True
    graph.review_events[0].validate()
    graph.review_events[1].validate()


def test_mapping_proposer_cannot_self_approve_without_exception() -> None:
    mapping = SourceCurriculumMappingVersion(
        mapping_id="mapping-self-review",
        mapping_version_id="mappingver-self-review-v1",
        source_chunk_version_id=CHUNK_NUMBERS_ID,
        curriculum_node_version_id=NODE_NUMBERS_VERSION_ID,
        support_type=SupportType.DIRECT_SUPPORT.value,
        authority_tier="tier_1",
        language="en",
        mapping_rationale="Self-review must require an explicit exception.",
        proposed_by="same_actor",
        proposed_at="2026-06-22T00:00:00+00:00",
    )
    with pytest.raises(Gate2R4ValidationError, match="proposer cannot be sole approver"):
        mapping.approve(reviewer_id="same_actor")
    approved = mapping.approve(reviewer_id="same_actor", exception_id="self-review-exception-2r4")
    assert approved.metadata["maker_checker_exception_id"] == "self-review-exception-2r4"


def test_language_translation_status_is_not_authority_by_default() -> None:
    mapping = SourceCurriculumMappingVersion(
        mapping_id="mapping-machine-translation",
        mapping_version_id="mappingver-machine-translation-v1",
        source_chunk_version_id=CHUNK_NUMBERS_ID,
        curriculum_node_version_id=NODE_NUMBERS_VERSION_ID,
        support_type=SupportType.DIRECT_SUPPORT.value,
        authority_tier="tier_1",
        language="af",
        language_status=LanguageAuthorityStatus.MACHINE_TRANSLATION_DRAFT.value,
        mapping_rationale="Machine translations cannot become Tier 1 authority.",
        proposed_by="translator",
        proposed_at="2026-06-22T00:00:00+00:00",
    )
    with pytest.raises(Gate2R4ValidationError, match="Machine translation draft|machine translation draft"):
        mapping.validate()


def test_graph_export_is_deterministic() -> None:
    first = export_gate2r4_reference_graph()
    second = export_gate2r4_reference_graph()
    assert first == second
    assert len(first["graph_sha256"]) == 64


def test_gate_2r4_does_not_authorise_gate_2r5() -> None:
    export = export_gate2r4_reference_graph()
    assert export["gate"] == "2R.4"
    assert export["boundary"]["corpus_activation"] is False
    assert export["boundary"]["retrieval_projection_rebuild"] is False
    assert export["boundary"]["generation_or_tutor_change"] is False
    assert "2R.5" not in str(export)


def test_reference_graph_validation_report_is_green() -> None:
    report = validate_gate2r4_reference_graph()
    assert report["valid"] is True
    assert report["tier1_support_validation"]["valid"] is True
    assert report["mapping_review_validation"]["valid"] is True
