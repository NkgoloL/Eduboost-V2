"""Comprehensive unit tests for Phase 02R Gate 2R.4 curriculum graph control layer enums and errors."""
from __future__ import annotations

import pytest

from app.services.curriculum.graph import (
    Gate2R4ValidationError,
    MappingRejectedError,
    ReviewStatus,
    NodeStatus,
    EdgeType,
    LanguageAuthorityStatus,
    SupportType,
    NODE_TYPES,
)


class TestCurriculumGraphEnumsAndErrors:
    def test_error_hierarchy(self):
        assert issubclass(MappingRejectedError, Gate2R4ValidationError)
        assert issubclass(Gate2R4ValidationError, ValueError)

        err = MappingRejectedError("Mapping rejected during review")
        assert "Mapping rejected" in str(err)

    def test_review_status_enums(self):
        assert ReviewStatus.PROPOSED == "proposed"
        assert ReviewStatus.IN_REVIEW == "in_review"
        assert ReviewStatus.APPROVED == "approved"
        assert ReviewStatus.REJECTED == "rejected"
        assert ReviewStatus.NEEDS_REVISION == "needs_revision"
        assert ReviewStatus.SUPERSEDED == "superseded"
        assert ReviewStatus.WITHDRAWN == "withdrawn"

    def test_node_status_enums(self):
        assert NodeStatus.DRAFT == "draft"
        assert NodeStatus.IN_REVIEW == "in_review"
        assert NodeStatus.APPROVED == "approved"
        assert NodeStatus.SUPERSEDED == "superseded"
        assert NodeStatus.WITHDRAWN == "withdrawn"

    def test_edge_types(self):
        assert EdgeType.PREREQUISITE_OF == "prerequisite_of"
        assert EdgeType.SEQUENCE_BEFORE == "sequence_before"
        assert EdgeType.SUPPORTS == "supports"
        assert EdgeType.ASSESSES == "assesses"
        assert EdgeType.SAME_CONCEPT_AS == "same_concept_as"
        assert EdgeType.TRANSLATION_OF == "translation_of"

    def test_language_authority_status_enums(self):
        assert LanguageAuthorityStatus.OFFICIAL_SOURCE == "official_source"
        assert LanguageAuthorityStatus.APPROVED_HUMAN_TRANSLATION == "approved_human_translation"
        assert LanguageAuthorityStatus.MACHINE_TRANSLATION_DRAFT == "machine_translation_draft"
        assert LanguageAuthorityStatus.GENERATED_LEARNER_EXPLANATION == "generated_learner_explanation"

    def test_support_types(self):
        assert SupportType.DIRECT_SUPPORT == "direct_support"
        assert SupportType.EXAMPLE == "example"
        assert SupportType.ASSESSMENT_EVIDENCE == "assessment_evidence"
        assert SupportType.TEACHING_GUIDANCE == "teaching_guidance"
        assert SupportType.BACKGROUND_CONTEXT == "background_context"

    def test_node_types_set(self):
        assert "curriculum" in NODE_TYPES
        assert "phase" in NODE_TYPES
        assert "grade" in NODE_TYPES
        assert "subject" in NODE_TYPES
        assert "topic" in NODE_TYPES
        assert "subtopic" in NODE_TYPES
