"""
Unit tests for app.services.irt_quality_service module.

Covers pure functions: _sigmoid, fit_two_parameter_logistic,
decide_intervention, correct_answer_position, answer_position_distribution.
Heavy async DB methods are excluded from this file; they require integration-
level fixtures not available here.
"""
from __future__ import annotations

from unittest.mock import MagicMock

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
    answer_position_distribution,
    correct_answer_position,
    decide_intervention,
    fit_two_parameter_logistic,
    IRTQualityError,
    IRTQualityConflict,
)


# ---------------------------------------------------------------------------
# _sigmoid
# ---------------------------------------------------------------------------

class TestSigmoid:
    def test_zero_returns_half(self):
        assert abs(_sigmoid(0.0) - 0.5) < 1e-6

    def test_large_positive_approaches_one(self):
        assert _sigmoid(100.0) > 0.999

    def test_large_negative_approaches_zero(self):
        assert _sigmoid(-100.0) < 0.001

    def test_symmetry(self):
        assert abs(_sigmoid(2.0) + _sigmoid(-2.0) - 1.0) < 1e-6

    def test_clamps_at_35(self):
        v1 = _sigmoid(35.0)
        v2 = _sigmoid(1000.0)
        assert abs(v1 - v2) < 1e-9


# ---------------------------------------------------------------------------
# fit_two_parameter_logistic
# ---------------------------------------------------------------------------

class TestFitTwoParameterLogistic:
    def _obs(self, ability, is_correct):
        obs = MagicMock(spec=IRTCalibrationObservation)
        obs.ability_proxy = ability
        obs.is_correct = is_correct
        return obs

    def test_empty_returns_defaults(self):
        a, b, rmse, converged = fit_two_parameter_logistic([])
        assert a == 1.0
        assert b == 0.0
        assert not converged

    def test_returns_four_tuple(self):
        obs = [self._obs(0.5, True), self._obs(-0.5, False)]
        result = fit_two_parameter_logistic(obs)
        assert len(result) == 4

    def test_parameters_in_valid_range(self):
        obs = [self._obs(float(i) * 0.3 - 1.0, i % 2 == 0) for i in range(10)]
        a, b, rmse, converged = fit_two_parameter_logistic(obs)
        assert 0.05 <= a <= 3.0
        assert -3.0 <= b <= 3.0
        assert 0.0 <= rmse <= 1.0

    def test_rmse_is_float(self):
        obs = [self._obs(1.0, True), self._obs(-1.0, False)]
        _, _, rmse, _ = fit_two_parameter_logistic(obs)
        assert isinstance(rmse, float)

    def test_convergence_flag(self):
        # A constant dataset should converge quickly
        obs = [self._obs(0.0, True)] * 50 + [self._obs(0.0, False)] * 50
        _, _, _, converged = fit_two_parameter_logistic(obs, iterations=300)
        assert isinstance(converged, bool)

    def test_custom_initial_params(self):
        obs = [self._obs(0.5, True), self._obs(-0.5, False)]
        a, b, _, _ = fit_two_parameter_logistic(obs, initial_a=2.0, initial_b=1.0)
        assert 0.05 <= a <= 3.0
        assert -3.0 <= b <= 3.0


# ---------------------------------------------------------------------------
# decide_intervention
# ---------------------------------------------------------------------------

def _default_policy():
    return IRTQualityPolicy()


def _healthy_metrics(**kwargs):
    base = dict(
        discrimination_a=1.2,
        difficulty_b=0.1,
        fit_rmse=0.15,
        accuracy=0.65,
        response_count=50,
        unique_learners=25,
        session_count=20,
        answered_ratio=0.92,
        guessing_c=0.25,
        converged=True,
        data_quality_passed=True,
        data_quality_reasons=[],
    )
    base.update(kwargs)
    return IRTCalibrationMetrics(**base)


class TestDecideIntervention:
    def test_healthy_item_retained(self):
        decision = decide_intervention(
            _healthy_metrics(),
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=_default_policy(),
        )
        assert decision.next_state == IRTQualityState.HEALTHY
        assert decision.action == IRTInterventionAction.RETAIN

    def test_poor_data_quality_no_change(self):
        metrics = _healthy_metrics(data_quality_passed=False, data_quality_reasons=["too_few_responses"])
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=_default_policy(),
        )
        assert decision.action == IRTInterventionAction.NONE
        assert decision.next_state == IRTQualityState.HEALTHY

    def test_override_active_suppresses_intervention(self):
        metrics = _healthy_metrics(discrimination_a=0.05)  # catastrophic
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.QUARANTINED,
            previous_strikes=5,
            policy=_default_policy(),
            override_active=True,
        )
        assert decision.action == IRTInterventionAction.NONE

    def test_catastrophic_first_strike_quarantines(self):
        metrics = _healthy_metrics(discrimination_a=0.1)  # below quarantine threshold
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=_default_policy(),
        )
        assert decision.next_state == IRTQualityState.QUARANTINED
        assert decision.action == IRTInterventionAction.QUARANTINE

    def test_catastrophic_enough_strikes_retires(self):
        metrics = _healthy_metrics(discrimination_a=0.1)  # catastrophic
        policy = _default_policy()
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.QUARANTINED,
            previous_strikes=policy.retire_after_strikes - 1,
            policy=policy,
        )
        assert decision.next_state == IRTQualityState.REWRITE_REVIEW
        assert decision.action == IRTInterventionAction.RETIRE
        assert decision.create_rewrite is True

    def test_weak_item_requires_review(self):
        # 0.40 is above quarantine_discrimination_max (0.35) but below monitor_discrimination_min (0.5)
        metrics = _healthy_metrics(discrimination_a=0.40)
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=_default_policy(),
        )
        assert decision.next_state == IRTQualityState.REVIEW_REQUIRED
        assert decision.action == IRTInterventionAction.REQUIRE_REVIEW

    def test_monitor_level_item(self):
        # Above monitor_discrimination_min (0.5) but below healthy (0.8)
        metrics = _healthy_metrics(discrimination_a=0.65)
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=2,
            policy=_default_policy(),
        )
        assert decision.next_state == IRTQualityState.MONITOR
        assert decision.action == IRTInterventionAction.MONITOR

    def test_high_rmse_triggers_weak_path(self):
        metrics = _healthy_metrics(fit_rmse=0.40)  # above max_fit_rmse=0.35
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=_default_policy(),
        )
        assert decision.next_state == IRTQualityState.REVIEW_REQUIRED

    def test_accuracy_too_low_catastrophic(self):
        metrics = _healthy_metrics(accuracy=0.05)  # below min_acceptable_accuracy
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=_default_policy(),
        )
        assert decision.next_state == IRTQualityState.QUARANTINED

    def test_accuracy_too_high_catastrophic(self):
        metrics = _healthy_metrics(accuracy=0.98)  # above max_acceptable_accuracy
        decision = decide_intervention(
            metrics,
            previous_state=IRTQualityState.HEALTHY,
            previous_strikes=0,
            policy=_default_policy(),
        )
        assert decision.next_state == IRTQualityState.QUARANTINED


# ---------------------------------------------------------------------------
# correct_answer_position
# ---------------------------------------------------------------------------

def _make_item(options, answer_key):
    item = MagicMock()
    item.options = options
    item.answer_key = answer_key
    return item


class TestCorrectAnswerPosition:
    def test_string_options(self):
        item = _make_item(["A", "B", "C", "D"], "C")
        assert correct_answer_position(item) == 2

    def test_dict_options_value_key(self):
        options = [{"value": "x"}, {"value": "y"}, {"value": "z"}]
        item = _make_item(options, "y")
        assert correct_answer_position(item) == 1

    def test_dict_options_text_key(self):
        options = [{"text": "alpha"}, {"text": "beta"}]
        item = _make_item(options, "alpha")
        assert correct_answer_position(item) == 0

    def test_answer_not_found_returns_none(self):
        item = _make_item(["A", "B", "C"], "D")
        assert correct_answer_position(item) is None

    def test_empty_options_returns_none(self):
        item = _make_item([], "A")
        assert correct_answer_position(item) is None

    def test_none_options_returns_none(self):
        item = _make_item(None, "A")
        assert correct_answer_position(item) is None


# ---------------------------------------------------------------------------
# answer_position_distribution
# ---------------------------------------------------------------------------

class TestAnswerPositionDistribution:
    def _item(self, options, answer_key):
        return _make_item(options, answer_key)

    def test_empty_returns_zero_sample(self):
        result = answer_position_distribution([])
        assert result["sample_size"] == 0

    def test_uniform_distribution(self):
        items = [
            self._item(["A", "B", "C", "D"], "A"),
            self._item(["A", "B", "C", "D"], "B"),
            self._item(["A", "B", "C", "D"], "C"),
            self._item(["A", "B", "C", "D"], "D"),
        ]
        result = answer_position_distribution(items)
        assert result["sample_size"] == 4
        assert len(result["shares"]) == 4

    def test_skewed_position(self):
        items = [self._item(["A", "B"], "A")] * 3 + [self._item(["A", "B"], "B")]
        result = answer_position_distribution(items)
        assert result["sample_size"] == 4
        assert float(result["shares"]["0"]) == pytest.approx(0.75)

    def test_shares_sum_to_one(self):
        items = [
            self._item(["X", "Y", "Z"], "X"),
            self._item(["X", "Y", "Z"], "Y"),
            self._item(["X", "Y", "Z"], "Z"),
        ]
        result = answer_position_distribution(items)
        total = sum(float(v) for v in result["shares"].values())
        assert abs(total - 1.0) < 1e-9

    def test_items_with_no_match_excluded(self):
        items = [
            self._item(["A", "B"], "A"),
            self._make_no_match_item(),
        ]
        result = answer_position_distribution(items)
        assert result["sample_size"] == 1

    def _make_no_match_item(self):
        return _make_item(["A", "B"], "MISSING")


# ---------------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------------

class TestExceptionClasses:
    def test_irt_quality_error_is_runtime_error(self):
        with pytest.raises(RuntimeError):
            raise IRTQualityError("test error")

    def test_irt_quality_conflict_is_irt_error(self):
        with pytest.raises(IRTQualityError):
            raise IRTQualityConflict("conflict")
