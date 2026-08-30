"""Comprehensive unit tests for Phase 4 IRT calibration and quality calculations."""
from __future__ import annotations

import math
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.irt_quality_service import (
    _sigmoid,
    fit_two_parameter_logistic,
    IRTQualityError,
    IRTQualityConflict,
)
from app.domain.irt_quality_schemas import (
    IRTCalibrationObservation,
    IRTQualityPolicy,
    IRTQualityState,
    IRTInterventionAction,
)


class TestIRTSigmoid:
    def test_sigmoid_zero(self):
        assert math.isclose(_sigmoid(0.0), 0.5, rel_tol=1e-5)

    def test_sigmoid_clipping(self):
        assert math.isclose(_sigmoid(100.0), 1.0, rel_tol=1e-5)
        assert math.isclose(_sigmoid(-100.0), 0.0, abs_tol=1e-5)


class TestIRT2PLFitting:
    def test_fit_empty_observations(self):
        a, b, loss, converged = fit_two_parameter_logistic(
            observations=[],
            initial_a=1.0,
            initial_b=0.0,
        )
        assert a == 1.0
        assert b == 0.0
        assert converged is False

    def test_fit_synthetic_observations(self):
        obs = [
            IRTCalibrationObservation(
                learner_id=uuid.uuid4(),
                session_id=uuid.uuid4(),
                ability_proxy=-1.0 if i < 20 else (0.0 if i < 40 else 1.0),
                is_correct=(i >= 30),
            )
            for i in range(60)
        ]
        a, b, loss, converged = fit_two_parameter_logistic(
            obs,
            initial_a=1.0,
            initial_b=0.0,
            iterations=50,
        )
        assert isinstance(a, float)
        assert isinstance(b, float)
        assert isinstance(loss, float)
        assert a > 0.0


class TestIRTQualityPolicy:
    def test_policy_defaults(self):
        policy = IRTQualityPolicy()
        assert policy.policy_version == "phase4-v1"
        assert policy.min_responses == 100
        assert policy.min_unique_learners == 50

    def test_quality_error_hierarchy(self):
        err = IRTQualityConflict("Item is locked")
        assert isinstance(err, IRTQualityError)
