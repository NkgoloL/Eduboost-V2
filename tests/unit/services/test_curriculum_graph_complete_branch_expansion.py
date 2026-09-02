import pytest
from app.services.curriculum.graph import (
    Gate2R4ValidationError,
    MappingRejectedError,
    ReviewStatus,
    NodeStatus,
    EdgeType,
    LanguageAuthorityStatus,
    SupportType,
    GraphNodeDraft,
    MappingDraft,
    CurriculumNodeVersion,
    CurriculumEdgeVersion,
    SourceCurriculumMappingVersion,
    MappingReviewEvent,
    CurriculumLanguageLink,
    Gate2R4CurriculumGraph,
    build_grade4_mathematics_skeleton,
    build_gate2r4_reference_graph,
    validate_gate2r4_reference_graph,
    export_gate2r4_reference_graph,
    ensure_no_gate2r5_scope,
    _uuid,
    _now,
    _canonical_json,
    _sha256_json,
    _coerce_review_status,
    _coerce_language_status,
    _coerce_edge_type,
)


def test_skeleton_and_reference_graph():
    skeleton = build_grade4_mathematics_skeleton()
    assert len(skeleton) == 8
    assert any(n.code == "CAPS" for n in skeleton)

    ref_graph = build_gate2r4_reference_graph()
    assert len(ref_graph.node_versions) == 2
    assert len(ref_graph.edge_versions) == 1
    assert len(ref_graph.mapping_versions) == 2

    report = validate_gate2r4_reference_graph()
    assert report["valid"] is True
    assert report["gate"] == "2R.4"

    export_data = export_gate2r4_reference_graph()
    assert export_data["schema"] == "edu_boost.phase02r.gate2r4.curriculum_graph_export.v1"
    assert "graph_sha256" in export_data


def test_ensure_no_gate2r5_scope():
    allowed_paths = [
        "app/services/curriculum/graph.py",
        "app/models/curriculum_graph.py",
        "scripts/verify_phase02r_gate2r4.py",
    ]
    assert ensure_no_gate2r5_scope(allowed_paths) == []

    forbidden_paths = [
        "app/services/semantic_retrieval/index.py",
        "app/models/corpus_activation.py",
        "scripts/embedding_rebuild.py",
    ]
    violations = ensure_no_gate2r5_scope(forbidden_paths)
    assert len(violations) == 3


def test_graph_node_draft_validation_edges():
    # Invalid language
    draft_bad_lang = GraphNodeDraft("topic", "T1", "Label", language="invalid_lang")
    with pytest.raises(MappingRejectedError, match="invalid language"):
        draft_bad_lang.validate()

    # Empty code
    draft_empty_code = GraphNodeDraft("topic", "", "Label")
    with pytest.raises(MappingRejectedError, match="code and label are required"):
        draft_empty_code.validate()

    # Empty label
    draft_empty_label = GraphNodeDraft("topic", "T1", "   ")
    with pytest.raises(MappingRejectedError, match="code and label are required"):
        draft_empty_label.validate()


def test_mapping_draft_validation_edges():
    # Invalid relationship type
    md_bad_rel = MappingDraft("c1", "n1", "INVALID_REL", "heuristic", ReviewStatus.APPROVED.value, "r1", "2026-01-01")
    with pytest.raises(MappingRejectedError, match="invalid relationship_type"):
        md_bad_rel.validate_for_retrieval()

    # Missing reviewer metadata
    md_no_rev = MappingDraft("c1", "n1", "supports", "heuristic", ReviewStatus.APPROVED.value, None, None)
    with pytest.raises(MappingRejectedError, match="reviewer metadata"):
        md_no_rev.validate_for_retrieval()



def test_curriculum_node_version_validation_edges():
    base_kwargs = dict(
        curriculum_node_id="n1",
        curriculum_node_version_id="n1-v1",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATHS",
        strand="Numbers",
        term="1",
        topic="Addition",
        subtopic="2-digit",
        skill="Add",
        learning_objective="Learners add numbers.",
        assessment_statement="Can add numbers",
        language="en",
        status=NodeStatus.DRAFT.value,
    )

    # 1. Invalid node_type
    with pytest.raises(Gate2R4ValidationError, match="invalid node_type"):
        CurriculumNodeVersion(**{**base_kwargs, "node_type": "invalid_type"}).validate()

    # 2. Invalid language
    with pytest.raises(Gate2R4ValidationError, match="invalid language"):
        CurriculumNodeVersion(**{**base_kwargs, "language": "es"}).validate()

    # 3. Invalid grade
    with pytest.raises(Gate2R4ValidationError, match="grade must be between 0 and 12"):
        CurriculumNodeVersion(**{**base_kwargs, "grade": 15}).validate()

    # 4. Empty curriculum_code or subject_code
    with pytest.raises(Gate2R4ValidationError, match="curriculum_code and subject_code are required"):
        CurriculumNodeVersion(**{**base_kwargs, "curriculum_code": " "}).validate()

    # 5. Empty strand or topic
    with pytest.raises(Gate2R4ValidationError, match="strand and topic are required"):
        CurriculumNodeVersion(**{**base_kwargs, "strand": ""}).validate()

    # 6. Empty learning_objective
    with pytest.raises(Gate2R4ValidationError, match="learning_objective is required"):
        CurriculumNodeVersion(**{**base_kwargs, "learning_objective": " "}).validate()

    # 7. Invalid status
    with pytest.raises(Gate2R4ValidationError, match="invalid node status"):
        CurriculumNodeVersion(**{**base_kwargs, "status": "unknown_status"}).validate()

    # 8. effective_to < effective_from
    with pytest.raises(Gate2R4ValidationError, match="effective_to cannot be before effective_from"):
        CurriculumNodeVersion(**{**base_kwargs, "effective_from": "2026-06-01", "effective_to": "2026-05-01"}).validate()

    # 9. Supersedes itself
    with pytest.raises(Gate2R4ValidationError, match="node version cannot supersede itself"):
        CurriculumNodeVersion(**{**base_kwargs, "supersedes_version_id": "n1-v1"}).validate()

    # 10. with_changes when approved raises error
    approved_node = CurriculumNodeVersion(**{**base_kwargs, "status": NodeStatus.APPROVED.value})
    with pytest.raises(Gate2R4ValidationError, match="approved curriculum node versions are immutable"):
        approved_node.with_changes(skill="New skill")

    # with_changes when draft succeeds
    draft_node = CurriculumNodeVersion(**base_kwargs)
    updated_node = draft_node.with_changes(skill="New skill")
    assert updated_node.skill == "New skill"

    # 11. approved without reviewer_id raises error
    with pytest.raises(Gate2R4ValidationError, match="reviewer_id is required"):
        draft_node.approved(effective_from="2026-01-01", reviewer_id="")

    # approved with reviewer_id succeeds
    approved_res = draft_node.approved(effective_from="2026-01-01", reviewer_id="rev-1")
    assert approved_res.is_approved is True
    assert approved_res.is_caps_requirement is True

    # 12. export
    export_dict = draft_node.export()
    assert export_dict["curriculum_node_id"] == "n1"


def test_curriculum_edge_version_validation_edges():
    # 1. Same from/to endpoints
    edge_same = CurriculumEdgeVersion("e1", "n1", "n1", EdgeType.SUPPORTS.value)
    with pytest.raises(Gate2R4ValidationError, match="edge endpoints must be different"):
        edge_same.validate()

    # 2. Unknown node version references
    edge_unknown = CurriculumEdgeVersion("e1", "n1", "n2", EdgeType.SUPPORTS.value)
    with pytest.raises(Gate2R4ValidationError, match="edge references unknown node versions"):
        edge_unknown.validate(existing_node_version_ids=["n1"])

    # 3. Approved without reviewed_by/at
    edge_app_no_rev = CurriculumEdgeVersion("e1", "n1", "n2", EdgeType.SUPPORTS.value, review_status=ReviewStatus.APPROVED.value)
    with pytest.raises(Gate2R4ValidationError, match="approved edge requires reviewed_by and reviewed_at"):
        edge_app_no_rev.validate()

    # 4. Supersedes itself
    edge_self_sup = CurriculumEdgeVersion(
        "e1", "n1", "n2", EdgeType.SUPPORTS.value,
        review_status=ReviewStatus.APPROVED.value,
        reviewed_by="rev1",
        reviewed_at="2026-01-01",
        supersedes_edge_version_id="e1",
    )
    with pytest.raises(Gate2R4ValidationError, match="edge version cannot supersede itself"):
        edge_self_sup.validate()

    # 5. approve() proposer cannot be sole approver without exception
    edge_prop = CurriculumEdgeVersion("e1", "n1", "n2", EdgeType.SUPPORTS.value, proposed_by="actor-1")
    with pytest.raises(Gate2R4ValidationError, match="proposer cannot be sole approver"):
        edge_prop.approve(reviewer_id="actor-1")

    # With exception_id succeeds
    approved_edge = edge_prop.approve(reviewer_id="actor-1", exception_id="exc-1")
    assert approved_edge.is_approved is True
    assert approved_edge.metadata["maker_checker_exception_id"] == "exc-1"
    assert approved_edge.export()["edge_version_id"] == "e1"


def test_source_curriculum_mapping_version_validation_edges():
    base_mapping = dict(
        mapping_id="m1",
        mapping_version_id="m1-v1",
        source_chunk_version_id="c1",
        curriculum_node_version_id="n1",
        support_type=SupportType.DIRECT_SUPPORT.value,
        authority_tier="tier_1",
        language="en",
        mapping_rationale="Solid curriculum coverage rationale.",
        proposed_by="prop-1",
        proposed_at="2026-01-01T00:00:00Z",
        review_status=ReviewStatus.PROPOSED.value,
    )

    # 1. Invalid support_type
    with pytest.raises(Gate2R4ValidationError, match="invalid support_type"):
        SourceCurriculumMappingVersion(**{**base_mapping, "support_type": "invalid_supp"}).validate()

    # 2. Invalid authority_tier
    with pytest.raises(Gate2R4ValidationError, match="invalid authority_tier"):
        SourceCurriculumMappingVersion(**{**base_mapping, "authority_tier": "tier_99"}).validate()

    # 3. Invalid language
    with pytest.raises(Gate2R4ValidationError, match="invalid language"):
        SourceCurriculumMappingVersion(**{**base_mapping, "language": "fr"}).validate()

    # 4. Empty rationale or proposed_by
    with pytest.raises(Gate2R4ValidationError, match="mapping_rationale is required"):
        SourceCurriculumMappingVersion(**{**base_mapping, "mapping_rationale": "  "}).validate()

    with pytest.raises(Gate2R4ValidationError, match="proposed_by is required"):
        SourceCurriculumMappingVersion(**{**base_mapping, "proposed_by": ""}).validate()

    # 5. Approved without reviewer metadata
    with pytest.raises(Gate2R4ValidationError, match="approved mapping requires reviewed_by and reviewed_at"):
        SourceCurriculumMappingVersion(**{**base_mapping, "review_status": ReviewStatus.APPROVED.value}).validate()

    # 6. Self-approval without exception
    with pytest.raises(Gate2R4ValidationError, match="mapping proposer cannot be sole approver"):
        SourceCurriculumMappingVersion(
            **{
                **base_mapping,
                "review_status": ReviewStatus.APPROVED.value,
                "reviewed_by": "prop-1",
                "reviewed_at": "2026-01-01T01:00:00Z",
            }
        ).validate()

    # 7. Machine translation draft cannot provide Tier 1 authority
    with pytest.raises(Gate2R4ValidationError, match="machine translation draft cannot provide Tier 1 authority"):
        SourceCurriculumMappingVersion(
            **{
                **base_mapping,
                "authority_tier": "tier_1",
                "language_status": LanguageAuthorityStatus.MACHINE_TRANSLATION_DRAFT.value,
            }
        ).validate()

    # 8. Supersedes itself
    with pytest.raises(Gate2R4ValidationError, match="mapping version cannot supersede itself"):
        SourceCurriculumMappingVersion(**{**base_mapping, "supersedes_mapping_version_id": "m1-v1"}).validate()

    # 9. Unknown chunk / node
    m = SourceCurriculumMappingVersion(**base_mapping)
    with pytest.raises(Gate2R4ValidationError, match="mapping references unknown source chunk"):
        m.validate(existing_source_chunk_version_ids=["c2"], existing_curriculum_node_version_ids=["n1"])

    with pytest.raises(Gate2R4ValidationError, match="mapping references unknown curriculum node version"):
        m.validate(existing_source_chunk_version_ids=["c1"], existing_curriculum_node_version_ids=["n2"])

    # 10. move_to_review branches
    in_review = m.move_to_review()
    assert in_review.review_status == ReviewStatus.IN_REVIEW.value
    with pytest.raises(Gate2R4ValidationError, match="only proposed or needs_revision"):
        in_review.move_to_review()

    # 11. reject requires review_notes
    with pytest.raises(Gate2R4ValidationError, match="rejection requires review_notes"):
        m.reject(reviewer_id="rev-1", review_notes="   ")
    rejected = m.reject(reviewer_id="rev-1", review_notes="Not aligned")
    assert rejected.review_status == ReviewStatus.REJECTED.value

    # 12. approve self without exception raises error; with exception succeeds
    with pytest.raises(Gate2R4ValidationError, match="mapping proposer cannot be sole approver"):
        m.approve(reviewer_id="prop-1")
    approved = m.approve(reviewer_id="rev-2", review_notes="Looks great")
    assert approved.corpus_eligible is True
    assert approved.tier1_approved is True
    assert approved.export()["mapping_id"] == "m1"


def test_mapping_review_event_and_language_link_edges():
    # 1. MappingReviewEvent invalid event_type
    with pytest.raises(Gate2R4ValidationError, match="invalid mapping review event_type"):
        MappingReviewEvent("ev-1", "m1", "unknown_event", "actor-1", "2026-01-01").validate()

    # 2. Missing mapping_version_id or actor_id
    with pytest.raises(Gate2R4ValidationError, match="requires mapping_version_id and actor_id"):
        MappingReviewEvent("ev-1", "", "approved", "actor-1", "2026-01-01").validate()

    # 3. Approved event without per_item_trace_id
    with pytest.raises(Gate2R4ValidationError, match="approval event requires a per-item trace id"):
        MappingReviewEvent("ev-1", "m1", "approved", "actor-1", "2026-01-01").validate()

    valid_event = MappingReviewEvent("ev-1", "m1", "approved", "actor-1", "2026-01-01", per_item_trace_id="trace-1")
    valid_event.validate()
    assert valid_event.export()["review_event_id"] == "ev-1"

    # 4. CurriculumLanguageLink endpoints must differ
    with pytest.raises(Gate2R4ValidationError, match="language link endpoints must differ"):
        CurriculumLanguageLink("ll-1", "n1", "n1", LanguageAuthorityStatus.OFFICIAL_SOURCE.value, "user-1").validate()

    # 5. Unknown node references
    link = CurriculumLanguageLink("ll-1", "n1", "n2", LanguageAuthorityStatus.OFFICIAL_SOURCE.value, "user-1")
    with pytest.raises(Gate2R4ValidationError, match="language link references unknown node versions"):
        link.validate(existing_node_version_ids=["n1"])

    # 6. Machine translation draft cannot be approved as official authority
    link_mt_app = CurriculumLanguageLink(
        "ll-1", "n1", "n2",
        LanguageAuthorityStatus.MACHINE_TRANSLATION_DRAFT.value,
        "user-1",
        review_status=ReviewStatus.APPROVED.value,
    )
    with pytest.raises(Gate2R4ValidationError, match="cannot be approved as official authority"):
        link_mt_app.validate()
    assert link.export()["language_link_id"] == "ll-1"


def test_gate2r4_curriculum_graph_operations_and_reports():
    graph = Gate2R4CurriculumGraph()

    # 1. add_source_chunk empty raises error
    with pytest.raises(Gate2R4ValidationError, match="chunk_version_id is required"):
        graph.add_source_chunk("")

    graph.add_source_chunk("c1", page_id="p1", section_id="s1")

    # 2. add_node_version duplicate raises error
    node = CurriculumNodeVersion(
        curriculum_node_id="n1",
        curriculum_node_version_id="n1-v1",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATHS",
        strand="Numbers",
        term="1",
        topic="Addition",
        subtopic="2-digit",
        skill="Add",
        learning_objective="Learners add numbers.",
        assessment_statement="Can add numbers",
        language="en",
        status=NodeStatus.APPROVED.value,
        effective_from="2026-01-01",
    )
    graph.add_node_version(node)
    with pytest.raises(Gate2R4ValidationError, match="duplicate node version"):
        graph.add_node_version(node)

    # 3. propose_mapping_from_client with forbidden approval fields
    with pytest.raises(Gate2R4ValidationError, match="client cannot supply approval fields"):
        graph.propose_mapping_from_client(
            source_chunk_version_id="c1",
            curriculum_node_version_id="n1-v1",
            mapping_rationale="Direct link",
            proposed_by="mapper-1",
            approved=True,
        )

    # Valid client proposal
    mapping = graph.propose_mapping_from_client(
        source_chunk_version_id="c1",
        curriculum_node_version_id="n1-v1",
        mapping_rationale="Direct link to CAPS objective",
        proposed_by="mapper-1",
    )
    assert mapping.review_status == ReviewStatus.PROPOSED.value
    assert len(graph.review_events) == 1

    # Duplicate mapping raises error
    with pytest.raises(Gate2R4ValidationError, match="duplicate mapping version"):
        graph.add_mapping_version(mapping)

    # 4. review_mapping unsupported decision
    with pytest.raises(Gate2R4ValidationError, match="unsupported mapping review decision"):
        graph.review_mapping(mapping.mapping_version_id, reviewer_id="rev-1", decision="invalid_decision")

    # review_mapping needs_revision
    revised = graph.review_mapping(
        mapping.mapping_version_id,
        reviewer_id="rev-1",
        decision="needs_revision",
        review_notes="Add more context",
    )
    assert revised.review_status == "needs_revision"

    # review_mapping approved
    approved = graph.review_mapping(
        mapping.mapping_version_id,
        reviewer_id="rev-1",
        decision="approved",
        review_notes="Approved now",
    )
    assert approved.review_status == ReviewStatus.APPROVED.value

    # review_mapping rejected
    rejected = graph.review_mapping(
        mapping.mapping_version_id,
        reviewer_id="rev-1",
        decision="rejected",
    )
    assert rejected.review_status == ReviewStatus.REJECTED.value

    # 5. add_language_link
    node2 = CurriculumNodeVersion(
        curriculum_node_id="n2",
        curriculum_node_version_id="n2-v1",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATHS",
        strand="Numbers",
        term="1",
        topic="Addition",
        subtopic="2-digit",
        skill="Add",
        learning_objective="Learners add numbers in Afrikaans.",
        assessment_statement="Can add numbers",
        language="af",
        status=NodeStatus.APPROVED.value,
        effective_from="2026-01-01",
    )
    graph.add_node_version(node2)

    link = CurriculumLanguageLink(
        language_link_id="link-1",
        source_node_version_id="n1-v1",
        target_node_version_id="n2-v1",
        language_status=LanguageAuthorityStatus.APPROVED_HUMAN_TRANSLATION.value,
        created_by="trans-1",
    )
    graph.add_language_link(link)
    assert len(graph.language_links) == 1

    # 6. validation report
    report = graph.validation_report()
    assert "counts" in report
    assert report["counts"]["source_chunks"] == 1
    assert report["counts"]["node_versions"] == 2
    assert report["counts"]["mapping_versions"] == 1
    assert report["counts"]["language_links"] == 1
