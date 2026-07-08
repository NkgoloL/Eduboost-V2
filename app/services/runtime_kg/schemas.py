"""Typed runtime KG contracts used by loaders, projections, and integration hooks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeKGNodeInput:
    stable_code: str
    label: str
    node_type: str = "skill"
    curriculum_code: str = "CAPS"
    grade: int = 4
    subject_code: str = "Mathematics"
    strand: str | None = None
    topic: str | None = None
    mastery_weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeKGEdgeInput:
    from_stable_code: str
    to_stable_code: str
    edge_type: str = "prerequisite_of"
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeKGGraphInput:
    graph_version: str
    source_ref: str
    source_sha256: str
    loaded_by: str
    curriculum_code: str = "CAPS"
    grade: int = 4
    subject_code: str = "Mathematics"
    nodes: tuple[RuntimeKGNodeInput, ...] = ()
    edges: tuple[RuntimeKGEdgeInput, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearnerEvidence:
    stable_code: str
    correct: bool
    confidence: float = 0.7
    evidence_source: str = "diagnostic"


@dataclass(frozen=True)
class LearnerKGNodeProjection:
    stable_code: str
    label: str
    mastery_score: float
    confidence: float
    gap_open: bool
    evidence_count: int


@dataclass(frozen=True)
class RuntimeKGProjection:
    learner_id: str
    subject_code: str
    graph_version: str
    nodes: tuple[LearnerKGNodeProjection, ...]

    @property
    def open_gaps(self) -> tuple[LearnerKGNodeProjection, ...]:
        return tuple(node for node in self.nodes if node.gap_open)

    def lesson_context(self, limit: int = 3) -> dict[str, Any]:
        gaps = sorted(self.open_gaps, key=lambda node: (node.mastery_score, -node.confidence))[:limit]
        return {
            "runtime_kg_enabled": True,
            "graph_version": self.graph_version,
            "knowledge_gaps": [
                {"topic": gap.label, "stable_code": gap.stable_code, "severity": round(1.0 - gap.mastery_score, 4)}
                for gap in gaps
            ],
        }

    def study_plan_focus(self, limit: int = 5) -> list[dict[str, Any]]:
        gaps = sorted(self.open_gaps, key=lambda node: (node.mastery_score, -node.confidence))[:limit]
        return [
            {
                "stable_code": gap.stable_code,
                "focus": gap.label,
                "mastery_score": gap.mastery_score,
                "recommended_action": "diagnose_prerequisite" if gap.confidence < 0.5 else "targeted_practice",
            }
            for gap in gaps
        ]
