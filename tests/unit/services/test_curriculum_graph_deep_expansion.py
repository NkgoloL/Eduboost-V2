"""Comprehensive unit tests for Gate 2R.4 curriculum graph controls."""
from __future__ import annotations

import pytest

from app.services.curriculum.graph import (
    GraphNodeDraft,
    MappingRejectedError,
    ReviewStatus,
    NodeStatus,
    EdgeType,
    LanguageAuthorityStatus,
    SupportType,
    NODE_TYPES,
    LEGACY_RELATIONSHIP_TYPES,
    ALLOWED_LANGUAGES,
    AUTHORITY_TIERS,
)


class TestCurriculumGraphDraftValidation:
    def test_node_draft_valid(self):
        draft = GraphNodeDraft(
            node_type="topic",
            code="4.M.1.1",
            label="Whole Numbers",
            curriculum="CAPS",
            grade=4,
            subject="Mathematics",
            language="en",
        )
        draft.validate()  # Should not raise

    def test_node_draft_invalid_type(self):
        draft = GraphNodeDraft(
            node_type="invalid_type_xyz",
            code="4.M.1.1",
            label="Whole Numbers",
        )
        with pytest.raises(MappingRejectedError, match="invalid node_type"):
            draft.validate()

    def test_node_draft_invalid_language(self):
        draft = GraphNodeDraft(
            node_type="topic",
            code="4.M.1.1",
            label="Whole Numbers",
            language="invalid_lang",
        )
        with pytest.raises(MappingRejectedError, match="invalid language"):
            draft.validate()


class TestCurriculumGraphEnumsAndConstants:
    def test_review_status_enums(self):
        assert ReviewStatus.PROPOSED.value == "proposed"
        assert ReviewStatus.APPROVED.value == "approved"
        assert ReviewStatus.REJECTED.value == "rejected"

    def test_edge_types(self):
        assert EdgeType.PREREQUISITE_OF.value == "prerequisite_of"
        assert EdgeType.SUPPORTS.value == "supports"
        assert EdgeType.ASSESSES.value == "assesses"

    def test_constants_membership(self):
        assert "topic" in NODE_TYPES
        assert "skill" in NODE_TYPES
        assert "CONTAINS" in LEGACY_RELATIONSHIP_TYPES
        assert "en" in ALLOWED_LANGUAGES
        assert "tier_1" in AUTHORITY_TIERS
