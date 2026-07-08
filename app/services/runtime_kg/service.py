"""Runtime KG learner projection logic."""
from __future__ import annotations

from dataclasses import dataclass

from app.services.runtime_kg.schemas import LearnerEvidence, LearnerKGNodeProjection, RuntimeKGNodeInput, RuntimeKGProjection


@dataclass(frozen=True)
class RuntimeKGProjectionService:
    """Deterministic learner-state projection over runtime KG nodes."""

    mastery_threshold: float = 0.7

    def project_from_evidence(
        self,
        *,
        learner_id: str,
        subject_code: str,
        graph_version: str,
        nodes: list[RuntimeKGNodeInput],
        evidence: list[LearnerEvidence],
    ) -> RuntimeKGProjection:
        by_code = {node.stable_code: node for node in nodes}
        evidence_by_code: dict[str, list[LearnerEvidence]] = {}
        for item in evidence:
            if item.stable_code in by_code:
                evidence_by_code.setdefault(item.stable_code, []).append(item)
        projections: list[LearnerKGNodeProjection] = []
        for stable_code, node in sorted(by_code.items()):
            node_evidence = evidence_by_code.get(stable_code, [])
            if node_evidence:
                correct_ratio = sum(1 for item in node_evidence if item.correct) / len(node_evidence)
                avg_confidence = sum(max(0.0, min(1.0, item.confidence)) for item in node_evidence) / len(node_evidence)
                mastery_score = max(0.0, min(1.0, correct_ratio * avg_confidence))
                confidence = avg_confidence
            else:
                mastery_score = 0.0
                confidence = 0.0
            projections.append(
                LearnerKGNodeProjection(
                    stable_code=stable_code,
                    label=node.label,
                    mastery_score=round(mastery_score, 4),
                    confidence=round(confidence, 4),
                    gap_open=mastery_score < self.mastery_threshold,
                    evidence_count=len(node_evidence),
                )
            )
        return RuntimeKGProjection(
            learner_id=learner_id,
            subject_code=subject_code,
            graph_version=graph_version,
            nodes=tuple(projections),
        )
