import uuid
import pytest
from unittest.mock import MagicMock

from app.models.diagnostic_item import DiagnosticItem
from app.services.irt_quality_service import (
    _sigmoid,
    correct_answer_position,
    answer_position_distribution,
    IRTQualityPolicy,
    IRTQualityState,
    IRTInterventionAction,
    decide_intervention,
)
from app.domain.irt_quality_schemas import IRTCalibrationMetrics


def test_sigmoid_math():
    assert _sigmoid(0.0) == 0.5
    assert _sigmoid(100.0) > 0.999
    assert _sigmoid(-100.0) < 0.001


def test_answer_position_distribution():
    item1 = MagicMock(spec=DiagnosticItem)
    item1.options = ["A", "B", "C", "D"]
    item1.answer_key = "B"
    assert correct_answer_position(item1) == 1

    item2 = MagicMock(spec=DiagnosticItem)
    item2.options = [{"value": "A"}, {"value": "B"}]
    item2.answer_key = "A"
    assert correct_answer_position(item2) == 0

    dist = answer_position_distribution([item1, item2])
    assert dist["sample_size"] == 2
    assert 0 in dist["counts"]
    assert 1 in dist["counts"]


def test_decide_intervention_healthy():
    policy = IRTQualityPolicy()
    metrics = IRTCalibrationMetrics(
        response_count=100,
        unique_learners=80,
        session_count=50,
        answered_ratio=1.0,
        accuracy=0.65,
        guessing_c=0.25,
        data_quality_passed=True,
        data_quality_reasons=[],
        converged=True,
        discrimination_a=1.2,
        difficulty_b=0.1,
        fit_rmse=0.10,
    )
    decision = decide_intervention(
        metrics,
        previous_state=IRTQualityState.HEALTHY,
        previous_strikes=0,
        policy=policy,
    )
    assert decision.action == IRTInterventionAction.RETAIN
    assert decision.next_state == IRTQualityState.HEALTHY
