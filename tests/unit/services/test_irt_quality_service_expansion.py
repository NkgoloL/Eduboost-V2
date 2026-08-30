import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.domain.irt_quality_schemas import (
    IRTCalibrationDecision,
    IRTCalibrationMetrics,
    IRTCalibrationObservation,
    IRTInterventionAction,
    IRTQualityPolicy,
    IRTQualityState,
)
from app.models.diagnostic_item import DiagnosticItem
from app.services.irt_quality_service import (
    _sigmoid,
    fit_two_parameter_logistic,
    decide_intervention,
    correct_answer_position,
    answer_position_distribution,
    IRTQualityService,
    IRTQualityError,
    IRTQualityConflict,
)


def test_sigmoid_math():
    assert _sigmoid(0.0) == 0.5
    assert _sigmoid(100.0) == pytest.approx(1.0, rel=1e-3)
    assert _sigmoid(-100.0) == pytest.approx(0.0, abs=1e-3)


def test_fit_two_parameter_logistic_empty():
    a, b, rmse, converged = fit_two_parameter_logistic([])
    assert a == 1.0
    assert b == 0.0
    assert rmse == 1.0
    assert converged is False


def test_fit_two_parameter_logistic_with_data():
    observations = [
        IRTCalibrationObservation(
            learner_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            ability_proxy=-1.5,
            is_correct=False,
        ),
        IRTCalibrationObservation(
            learner_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            ability_proxy=-0.5,
            is_correct=False,
        ),
        IRTCalibrationObservation(
            learner_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            ability_proxy=0.5,
            is_correct=True,
        ),
        IRTCalibrationObservation(
            learner_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            ability_proxy=1.5,
            is_correct=True,
        ),
    ]
    a, b, rmse, converged = fit_two_parameter_logistic(observations, iterations=50)
    assert 0.05 <= a <= 3.0
    assert -3.0 <= b <= 3.0
    assert rmse >= 0.0


def test_decide_intervention_data_quality_failed():
    policy = IRTQualityPolicy()
    metrics = IRTCalibrationMetrics(
        response_count=5,
        unique_learners=5,
        session_count=2,
        answered_ratio=0.95,
        accuracy=0.5,
        discrimination_a=1.0,
        difficulty_b=0.0,
        guessing_c=0.25,
        fit_rmse=0.1,
        converged=True,
        data_quality_passed=False,
        data_quality_reasons=["sample size below minimum 50"],
    )

    decision = decide_intervention(
        metrics,
        previous_state=IRTQualityState.HEALTHY,
        previous_strikes=0,
        policy=policy,
    )
    assert decision.action == IRTInterventionAction.NONE
    assert decision.next_state == IRTQualityState.HEALTHY
    assert "insufficient_or_invalid_calibration_data" in decision.reason


def test_decide_intervention_healthy():
    policy = IRTQualityPolicy()
    metrics = IRTCalibrationMetrics(
        response_count=100,
        unique_learners=60,
        session_count=30,
        answered_ratio=0.98,
        accuracy=0.65,
        discrimination_a=1.2,
        difficulty_b=0.1,
        guessing_c=0.25,
        fit_rmse=0.08,
        converged=True,
        data_quality_passed=True,
    )

    decision = decide_intervention(
        metrics,
        previous_state=IRTQualityState.HEALTHY,
        previous_strikes=0,
        policy=policy,
    )
    assert decision.action == IRTInterventionAction.RETAIN
    assert decision.next_state == IRTQualityState.HEALTHY
    assert decision.update_parameters is True


def test_decide_intervention_catastrophic():
    policy = IRTQualityPolicy()
    metrics = IRTCalibrationMetrics(
        response_count=100,
        unique_learners=60,
        session_count=30,
        answered_ratio=0.98,
        accuracy=0.02,  # Catastrophic accuracy
        discrimination_a=0.1,
        difficulty_b=0.0,
        guessing_c=0.25,
        fit_rmse=0.5,
        converged=True,
        data_quality_passed=True,
    )

    decision = decide_intervention(
        metrics,
        previous_state=IRTQualityState.HEALTHY,
        previous_strikes=0,
        policy=policy,
    )
    assert decision.action == IRTInterventionAction.QUARANTINE
    assert decision.next_state == IRTQualityState.QUARANTINED
    assert decision.strike_count == 1


def test_answer_position_helpers():
    item1 = MagicMock(spec=DiagnosticItem)
    item1.options = ["A", "B", "C", "D"]
    item1.answer_key = "B"
    assert correct_answer_position(item1) == 1

    item2 = MagicMock(spec=DiagnosticItem)
    item2.options = [{"value": "opt1"}, {"value": "opt2"}]
    item2.answer_key = "opt1"
    assert correct_answer_position(item2) == 0

    dist = answer_position_distribution([item1, item2])
    assert dist["sample_size"] == 2
    assert "0" in dist["shares"]
    assert "1" in dist["shares"]
