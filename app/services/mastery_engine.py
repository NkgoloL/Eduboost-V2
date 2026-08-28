"""Versioned Mastery Engine with Programmatic Invariant Bounds (TSR-9).

Implements:
- Strict state semantics: 'tentative', 'inferred', 'stale', 'superseded'.
- Mathematical bounds: MAX_CONFIDENCE_THRESHOLD = 0.60 (prohibiting unvalidated 'authoritative' claims).
- Full provenance tagging: algorithm version, graph version, calculation timestamp.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional


class MasteryStateEnum(str, enum.Enum):
    TENTATIVE = "tentative"
    INFERRED = "inferred"
    STALE = "stale"
    SUPERSEDED = "superseded"
    # Note: 'authoritative' is strictly prohibited until longitudinal calibration gate RG-4
    AUTHORITATIVE = "authoritative"


# Strict mathematical ceiling for uncalibrated mastery estimates
MAX_CONFIDENCE_THRESHOLD: float = 0.60
CURRENT_ALGORITHM_VERSION: str = "v2.1.0-bounded"
CURRENT_GRAPH_VERSION: str = "2026.1-caps"


class MasteryBoundError(ValueError):
    """Raised when an operation attempts to violate mastery confidence invariants."""
    pass


@dataclass(frozen=True)
class MasteryEstimate:
    learner_id: str
    node_id: str
    mastery_score: float
    confidence: float
    state: MasteryStateEnum
    algorithm_version: str
    graph_version: str
    computed_at: str
    evidence_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "learner_id": self.learner_id,
            "node_id": self.node_id,
            "mastery_score": round(self.mastery_score, 4),
            "confidence": round(self.confidence, 4),
            "state": self.state.value,
            "algorithm_version": self.algorithm_version,
            "graph_version": self.graph_version,
            "computed_at": self.computed_at,
            "evidence_count": self.evidence_count,
        }


class MasteryEngine:
    """Computes and bounds learner mastery states across curriculum nodes."""

    def __init__(
        self,
        algorithm_version: str = CURRENT_ALGORITHM_VERSION,
        graph_version: str = CURRENT_GRAPH_VERSION,
        max_confidence: float = MAX_CONFIDENCE_THRESHOLD,
    ) -> None:
        self.algorithm_version = algorithm_version
        self.graph_version = graph_version
        self.max_confidence = max_confidence

    def calculate_node_mastery(
        self,
        learner_id: str,
        node_id: str,
        correct_responses: int,
        total_responses: int,
        prior_score: Optional[float] = None,
        is_prerequisite_inferred: bool = False,
    ) -> MasteryEstimate:
        """Compute bounded mastery estimate from observed response evidence."""
        if total_responses < 0 or correct_responses < 0 or correct_responses > total_responses:
            raise ValueError("Invalid response counts provided to mastery calculation.")

        now_utc = datetime.now(timezone.utc).isoformat()

        if total_responses == 0:
            if prior_score is not None:
                return MasteryEstimate(
                    learner_id=learner_id,
                    node_id=node_id,
                    mastery_score=min(prior_score, 1.0),
                    confidence=0.10,
                    state=MasteryStateEnum.TENTATIVE,
                    algorithm_version=self.algorithm_version,
                    graph_version=self.graph_version,
                    computed_at=now_utc,
                    evidence_count=0,
                )
            return MasteryEstimate(
                learner_id=learner_id,
                node_id=node_id,
                mastery_score=0.0,
                confidence=0.0,
                state=MasteryStateEnum.TENTATIVE,
                algorithm_version=self.algorithm_version,
                graph_version=self.graph_version,
                computed_at=now_utc,
                evidence_count=0,
            )

        # Baseline accuracy ratio
        raw_accuracy = correct_responses / total_responses

        # Raw sample-size confidence (asymptotic curve)
        raw_confidence = 1.0 - (1.0 / (1.0 + (total_responses * 0.25)))

        # Enforce hard-coded mathematical invariant ceiling
        bounded_confidence = min(raw_confidence, self.max_confidence)

        # State designation
        if is_prerequisite_inferred:
            state = MasteryStateEnum.INFERRED
        else:
            # All active direct estimates remain TENTATIVE until longitudinal validation
            state = MasteryStateEnum.TENTATIVE

        return MasteryEstimate(
            learner_id=learner_id,
            node_id=node_id,
            mastery_score=raw_accuracy,
            confidence=bounded_confidence,
            state=state,
            algorithm_version=self.algorithm_version,
            graph_version=self.graph_version,
            computed_at=now_utc,
            evidence_count=total_responses,
        )

    def assert_no_authoritative_claims(
        self,
        estimate: MasteryEstimate | dict[str, Any] | float | None = None,
        confidence: float | None = None,
        state: MasteryStateEnum | str | None = None,
    ) -> None:
        """Hard invariant guard: refuse to serialize or persist uncalibrated authoritative claims."""
        target_conf: float | None = confidence
        target_state: str | None = state.value if isinstance(state, MasteryStateEnum) else state


        if isinstance(estimate, MasteryEstimate):
            target_conf = estimate.confidence
            target_state = estimate.state.value
        elif isinstance(estimate, dict):
            target_conf = estimate.get("confidence", confidence)
            raw_st = estimate.get("state", target_state)
            target_state = raw_st.value if isinstance(raw_st, MasteryStateEnum) else (str(raw_st) if raw_st is not None else None)
        elif isinstance(estimate, (int, float)):
            target_conf = float(estimate)


        if target_state is not None and str(target_state).lower() == MasteryStateEnum.AUTHORITATIVE.value:
            raise MasteryBoundError(
                f"Educational Claim Violation: State '{target_state}' attempts unsupported 'authoritative' state."
            )

        if target_conf is not None and target_conf > (self.max_confidence + 1e-6):
            raise MasteryBoundError(
                f"Educational Claim Violation: Confidence {target_conf} exceeds approved "
                f"ceiling {self.max_confidence}."
            )


def assert_no_authoritative_claims(
    estimate: MasteryEstimate | dict[str, Any] | float | None = None,
    confidence: float | None = None,
    state: MasteryStateEnum | str | None = None,
    max_confidence: float = MAX_CONFIDENCE_THRESHOLD,
) -> None:
    """Module-level invariant guard refusing to serialize or persist uncalibrated authoritative claims."""
    engine = MasteryEngine(max_confidence=max_confidence)
    engine.assert_no_authoritative_claims(estimate=estimate, confidence=confidence, state=state)

