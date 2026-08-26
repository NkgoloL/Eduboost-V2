"""Unit tests for Versioned Mastery Engine Semantics & Bounds (TSR-9)."""
from __future__ import annotations

import pytest
from app.services.mastery_engine import (
    MasteryEngine,
    MasteryEstimate,
    MasteryStateEnum,
    MasteryBoundError,
    MAX_CONFIDENCE_THRESHOLD,
    CURRENT_ALGORITHM_VERSION,
    CURRENT_GRAPH_VERSION,
)


@pytest.mark.unit
def test_mastery_confidence_is_bounded_by_mathematical_ceiling():
    engine = MasteryEngine()

    # Even with high volume of evidence (e.g. 100 correct out of 100)
    estimate = engine.calculate_node_mastery(
        learner_id="learner-test-1",
        node_id="math-grade4-fractions-01",
        correct_responses=100,
        total_responses=100,
    )

    assert estimate.mastery_score == 1.0
    # Confidence MUST NOT exceed MAX_CONFIDENCE_THRESHOLD (0.60)
    assert estimate.confidence <= MAX_CONFIDENCE_THRESHOLD
    assert estimate.confidence == MAX_CONFIDENCE_THRESHOLD
    assert estimate.state == MasteryStateEnum.TENTATIVE
    assert estimate.algorithm_version == CURRENT_ALGORITHM_VERSION
    assert estimate.graph_version == CURRENT_GRAPH_VERSION


@pytest.mark.unit
def test_zero_response_cold_start():
    engine = MasteryEngine()

    estimate = engine.calculate_node_mastery(
        learner_id="learner-test-2",
        node_id="math-grade4-fractions-01",
        correct_responses=0,
        total_responses=0,
    )

    assert estimate.mastery_score == 0.0
    assert estimate.confidence == 0.0
    assert estimate.state == MasteryStateEnum.TENTATIVE
    assert estimate.evidence_count == 0


@pytest.mark.unit
def test_inferred_prerequisite_state():
    engine = MasteryEngine()

    estimate = engine.calculate_node_mastery(
        learner_id="learner-test-3",
        node_id="math-grade4-fractions-02",
        correct_responses=8,
        total_responses=10,
        is_prerequisite_inferred=True,
    )

    assert estimate.mastery_score == 0.8
    assert estimate.state == MasteryStateEnum.INFERRED
    assert estimate.confidence <= MAX_CONFIDENCE_THRESHOLD


@pytest.mark.unit
def test_assert_no_authoritative_claims_fails_closed():
    engine = MasteryEngine()

    # Legitimate bounded estimate passes
    valid_estimate = engine.calculate_node_mastery(
        learner_id="learner-test-4",
        node_id="math-grade4-fractions-01",
        correct_responses=5,
        total_responses=5,
    )
    engine.assert_no_authoritative_claims(valid_estimate)

    # Fabricated over-confident estimate must be rejected
    illegal_estimate = MasteryEstimate(
        learner_id="learner-test-5",
        node_id="math-grade4-fractions-01",
        mastery_score=0.95,
        confidence=0.99,
        state=MasteryStateEnum.AUTHORITATIVE,
        algorithm_version=CURRENT_ALGORITHM_VERSION,
        graph_version=CURRENT_GRAPH_VERSION,
        computed_at="2026-08-26T00:00:00Z",
        evidence_count=50,
    )

    with pytest.raises(MasteryBoundError, match="Educational Claim Violation"):
        engine.assert_no_authoritative_claims(illegal_estimate)
