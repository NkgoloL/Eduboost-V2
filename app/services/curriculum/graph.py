"""Curriculum graph and reviewed mapping helpers for Phase 2R Gate 2R.4."""
from __future__ import annotations

from dataclasses import dataclass, field

NODE_TYPES = frozenset({
    "curriculum", "phase", "grade", "subject", "term", "strand", "topic",
    "subtopic", "skill", "learning_objective", "assessment_requirement",
    "prerequisite", "vocabulary",
})
RELATIONSHIP_TYPES = frozenset({
    "CONTAINS", "REQUIRES", "PRECEDES", "DEPENDS_ON", "ASSESSED_BY",
    "EXEMPLIFIED_BY", "DEFINED_IN", "AMENDED_BY", "SUPERSEDES", "TRANSLATION_OF",
})


class MappingRejectedError(ValueError):
    pass


@dataclass(frozen=True)
class GraphNodeDraft:
    node_type: str
    code: str
    label: str
    curriculum: str = "CAPS"
    grade: int | None = 4
    subject: str | None = "Mathematics"
    language: str | None = "en"
    metadata: dict = field(default_factory=dict)

    def validate(self) -> None:
        if self.node_type not in NODE_TYPES:
            raise MappingRejectedError(f"invalid node_type: {self.node_type}")
        if self.language is not None and self.language not in {"en", "af", "nso"}:
            raise MappingRejectedError(f"invalid language: {self.language}")
        if self.grade is not None and not (0 <= self.grade <= 12):
            raise MappingRejectedError("grade must be between 0 and 12")
        if not self.code.strip() or not self.label.strip():
            raise MappingRejectedError("node code and label are required")


@dataclass(frozen=True)
class MappingDraft:
    chunk_version_id: str
    node_id: str
    relationship_type: str
    proposal_method: str
    review_status: str
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    def validate_for_retrieval(self) -> None:
        if self.relationship_type not in RELATIONSHIP_TYPES:
            raise MappingRejectedError(f"invalid relationship_type: {self.relationship_type}")
        if self.review_status != "approved":
            raise MappingRejectedError("mapping must be human-reviewed and approved")
        if not self.reviewed_by or not self.reviewed_at:
            raise MappingRejectedError("approved mapping requires reviewer metadata")


def build_grade4_mathematics_skeleton() -> list[GraphNodeDraft]:
    strands = [
        ("numbers_operations_relationships", "Numbers, operations and relationships"),
        ("patterns_functions_algebra", "Patterns, functions and algebra"),
        ("space_shape_geometry", "Space and shape"),
        ("measurement", "Measurement"),
        ("data_handling", "Data handling"),
    ]
    nodes = [
        GraphNodeDraft("curriculum", "CAPS", "CAPS"),
        GraphNodeDraft("grade", "GRADE_4", "Grade 4"),
        GraphNodeDraft("subject", "GRADE_4_MATHEMATICS", "Grade 4 Mathematics"),
    ]
    nodes.extend(GraphNodeDraft("strand", code.upper(), label) for code, label in strands)
    return nodes
