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
    _canonical_json,
    _sha256_json,
    _coerce_review_status,
    _coerce_language_status,
    _coerce_edge_type,
)


def test_enums_and_constants():
    assert ReviewStatus.APPROVED == "approved"
    assert NodeStatus.DRAFT == "draft"
    assert EdgeType.PREREQUISITE_OF == "prerequisite_of"
    assert LanguageAuthorityStatus.OFFICIAL_SOURCE == "official_source"
    assert SupportType.DIRECT_SUPPORT == "direct_support"


def test_graph_node_draft_validation():
    draft = GraphNodeDraft(
        node_type="learning_objective",
        code="CAPS-G4-M-01",
        label="Fractions addition",
        grade=4,
        language="en",
    )
    draft.validate()

    invalid_type = GraphNodeDraft(node_type="invalid_type", code="C", label="L")
    with pytest.raises(MappingRejectedError, match="invalid node_type"):
        invalid_type.validate()

    invalid_grade = GraphNodeDraft(node_type="topic", code="C", label="L", grade=15)
    with pytest.raises(MappingRejectedError, match="grade must be between 0 and 12"):
        invalid_grade.validate()


def test_mapping_draft_validation():
    mapping = MappingDraft(
        chunk_version_id="chunk-v1",
        node_id="node-1",
        relationship_type="supports",
        proposal_method="heuristic",
        review_status="approved",
        reviewed_by="teacher_1",
        reviewed_at="2026-08-29T12:00:00Z",
    )
    mapping.validate_for_retrieval()

    unapproved = MappingDraft(
        chunk_version_id="chunk-v1",
        node_id="node-1",
        relationship_type="supports",
        proposal_method="heuristic",
        review_status="proposed",
    )
    with pytest.raises(MappingRejectedError, match="must be human-reviewed"):
        unapproved.validate_for_retrieval()


def test_curriculum_node_version_validation():
    node = CurriculumNodeVersion(
        curriculum_node_id="node-1",
        curriculum_node_version_id="node-v1",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATHS",
        strand="Numbers",
        term="1",
        topic="Fractions",
        subtopic=None,
        skill="Addition",
        learning_objective="Add fractions with common denominators",
        assessment_statement=None,
        language="en",
    )
    node.validate()

    invalid_lang = CurriculumNodeVersion(
        curriculum_node_id="node-1",
        curriculum_node_version_id="node-v1",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATHS",
        strand="Numbers",
        term="1",
        topic="Fractions",
        subtopic=None,
        skill="Addition",
        learning_objective="Add fractions with common denominators",
        assessment_statement=None,
        language="invalid_language",
    )
    with pytest.raises(Gate2R4ValidationError, match="invalid language"):
        invalid_lang.validate()


def test_coercion_helpers():
    assert _coerce_review_status("approved") == ReviewStatus.APPROVED
    assert _coerce_language_status("official_source") == LanguageAuthorityStatus.OFFICIAL_SOURCE
    assert _coerce_edge_type("prerequisite_of") == EdgeType.PREREQUISITE_OF
    assert len(_sha256_json({"a": 1})) == 64
