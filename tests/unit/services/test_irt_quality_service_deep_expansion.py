"""Comprehensive unit tests for IRT quality policy and calibration decision engine."""
from __future__ import annotations

import uuid
import pytest

from app.domain.irt_quality_schemas import (
    IRTCalibrationMetrics,
    IRTCalibrationObservation,
    IRTInterventionAction,
    IRTQualityPolicy,
    IRTQualityState,
)
from app.services.irt_quality_service import (
    _sigmoid,
    fit_two_parameter_logistic,
    decide_intervention,
)


class TestIRTSigmoidAndFitting:
    def test_sigmoid_values(self):
        assert _sigmoid(0.0) == 0.5
        assert _sigmoid(100.0) == _sigmoid(35.0)
        assert _sigmoid(-100.0) == _sigmoid(-35.0)
        assert 0.0 < _sigmoid(-10.0) < 0.5 < _sigmoid(10.0) < 1.0

    def test_fit_empty_observations(self):
        a, b, rmse, converged = fit_two_parameter_logistic([], initial_a=1.2, initial_b=0.3)
        assert a == 1.2
        assert b == 0.3
        assert converged is False

    def test_fit_with_observations(self):
        obs = [
            IRTCalibrationObservation(
                learner_id=uuid.uuid4(),
                session_id=uuid.uuid4(),
                ability_proxy=1.0,
                is_correct=True,
            ),
            IRTCalibrationObservation(
                learner_id=uuid.uuid4(),
                session_id=uuid.uuid4(),
                ability_proxy=-1.0,
                is_correct=False,
            ),
            IRTCalibrationObservation(
                learner_id=uuid.uuid4(),
                session_id=uuid.uuid4(),
                ability_proxy=0.0,
                is_correct=True,
            ),
        ]
        a, b, rmse, converged = fit_two_parameter_logistic(obs, iterations=10)
        assert 0.05 <= a <= 3.0
        assert -3.0 <= b <= 3.0


class TestIRTCalibrationDecisions:
    def test_insufficient_data_quality(self):
        metrics = IRTCalibrationMetrics(
            response_count=5,
            unique_learners=5,
            session_count=2,
            answered_ratio=0.9,
            accuracy=0.8,
            discrimination_a=1.0,
            difficulty_b=0.0,
            guessing_c=0.25,
            fit_rmse=0.1,
            converged=True,
            data_quality_passed=False,
            data_quality_reasons=["min_exposures_not_met"],
        )
        policy = IRTQualityPolicy()
        dec = decide_intervention(
            metrics=metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=policy,
        )
        assert dec.action == IRTInterventionAction.NONE
        assert "insufficient" in dec.reason

    def test_active_manual_override_suppresses_intervention(self):
        metrics = IRTCalibrationMetrics(
            response_count=100,
            unique_learners=100,
            session_count=50,
            answered_ratio=0.98,
            accuracy=0.8,
            discrimination_a=0.20,  # below quarantine threshold 0.35
            difficulty_b=0.0,
            guessing_c=0.25,
            fit_rmse=0.48,  # above quarantine fit rmse 0.45
            converged=True,
            data_quality_passed=True,
        )
        policy = IRTQualityPolicy()
        dec = decide_intervention(
            metrics=metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=policy,
            override_active=True,
        )
        assert dec.action == IRTInterventionAction.NONE
        assert "manual override" in dec.reason

    def test_catastrophic_discrimination_triggers_quarantine(self):
        metrics = IRTCalibrationMetrics(
            response_count=100,
            unique_learners=100,
            session_count=50,
            answered_ratio=0.98,
            accuracy=0.8,
            discrimination_a=0.20,  # below quarantine threshold 0.35
            difficulty_b=0.0,
            guessing_c=0.25,
            fit_rmse=0.1,
            converged=True,
            data_quality_passed=True,
        )
        policy = IRTQualityPolicy()
        dec = decide_intervention(
            metrics=metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=policy,
        )
        assert dec.action == IRTInterventionAction.QUARANTINE
        assert dec.next_state == IRTQualityState.QUARANTINED
        assert dec.strike_count == 1
