from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from app.domain.irt_quality_schemas import (
    IRTCalibrationMetrics,
    IRTCalibrationObservation,
    IRTInterventionAction,
    IRTQualityPolicy,
    IRTQualityState,
)
from app.services.irt_quality_service import (
    answer_position_distribution,
    decide_intervention,
    fit_two_parameter_logistic,
)


def _metrics(*, a=1.0, rmse=0.2, accuracy=0.6, passed=True):
    return IRTCalibrationMetrics(
        response_count=120,
        unique_learners=70,
        session_count=60,
        answered_ratio=1.0,
        accuracy=accuracy,
        difficulty_b=0.0,
        discrimination_a=a,
        guessing_c=0.25,
        fit_rmse=rmse,
        converged=True,
        data_quality_passed=passed,
        data_quality_reasons=[] if passed else ["responses<100"],
    )


def test_policy_rejects_misordered_thresholds():
    try:
        IRTQualityPolicy(monitor_discrimination_min=0.3, quarantine_discrimination_max=0.4)
    except ValueError:
        pass
    else:
        raise AssertionError("misordered thresholds must be rejected")


def test_healthy_item_is_retained_and_strikes_reset():
    decision = decide_intervention(
        _metrics(a=1.2), previous_state=IRTQualityState.MONITOR,
        previous_strikes=2, policy=IRTQualityPolicy()
    )
    assert decision.action == IRTInterventionAction.RETAIN
    assert decision.next_state == IRTQualityState.HEALTHY
    assert decision.strike_count == 0
    assert decision.update_parameters is True


def test_weak_item_requires_review():
    decision = decide_intervention(
        _metrics(a=0.42), previous_state=IRTQualityState.HEALTHY,
        previous_strikes=0, policy=IRTQualityPolicy()
    )
    assert decision.action == IRTInterventionAction.REQUIRE_REVIEW
    assert decision.next_state == IRTQualityState.REVIEW_REQUIRED


def test_catastrophic_item_is_quarantined_then_rewrite_review():
    policy = IRTQualityPolicy()
    first = decide_intervention(
        _metrics(a=0.2), previous_state=IRTQualityState.HEALTHY,
        previous_strikes=0, policy=policy
    )
    assert first.next_state == IRTQualityState.QUARANTINED
    final = decide_intervention(
        _metrics(a=0.2), previous_state=IRTQualityState.QUARANTINED,
        previous_strikes=2, policy=policy
    )
    assert final.next_state == IRTQualityState.REWRITE_REVIEW
    assert final.create_rewrite is True


def test_insufficient_data_does_not_mutate_state():
    decision = decide_intervention(
        _metrics(passed=False), previous_state=IRTQualityState.HEALTHY,
        previous_strikes=1, policy=IRTQualityPolicy()
    )
    assert decision.action == IRTInterventionAction.NONE
    assert decision.next_state == IRTQualityState.HEALTHY
    assert decision.strike_count == 1


def test_manual_override_suppresses_automation():
    decision = decide_intervention(
        _metrics(a=0.1), previous_state=IRTQualityState.QUARANTINED,
        previous_strikes=2, policy=IRTQualityPolicy(), override_active=True
    )
    assert decision.next_state == IRTQualityState.QUARANTINED
    assert decision.create_rewrite is False


def test_fit_two_parameter_logistic_is_deterministic_and_bounded():
    observations = []
    for index in range(160):
        theta = -2.5 + 5.0 * index / 159
        correct = theta > -0.1
        observations.append(
            IRTCalibrationObservation(
                learner_id=uuid4(), session_id=uuid4(), ability_proxy=theta, is_correct=correct
            )
        )
    first = fit_two_parameter_logistic(observations)
    second = fit_two_parameter_logistic(observations)
    assert first == second
    a, b, rmse, _ = first
    assert 0.05 <= a <= 3.0
    assert -3.0 <= b <= 3.0
    assert rmse < 0.4


def test_answer_position_bias_is_measured_without_mutation():
    items = [
        SimpleNamespace(options=[{"value": "A"}, {"value": "B"}], answer_key="A")
        for _ in range(15)
    ] + [
        SimpleNamespace(options=[{"value": "A"}, {"value": "B"}], answer_key="B")
        for _ in range(5)
    ]
    result = answer_position_distribution(items)
    assert result["sample_size"] == 20
    assert result["max_share"] == 0.75
    assert all(item.options[0]["value"] == "A" for item in items)
