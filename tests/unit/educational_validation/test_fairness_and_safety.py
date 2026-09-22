import pytest

from app.services.educational_validation.fairness import (
    compute_mantel_haenszel_dif,
    evaluate_educational_fairness,
)
from app.services.educational_validation.safety import (
    SafetySeverity,
    analyze_interaction_safety,
)


def test_evaluate_educational_fairness_parity():
    records = [
        {"quintile": 1, "language_group": "xh", "item_id": "i1", "score": 1, "ability_group": "high"},
        {"quintile": 2, "language_group": "xh", "item_id": "i1", "score": 1, "ability_group": "high"},
        {"quintile": 4, "language_group": "en", "item_id": "i1", "score": 1, "ability_group": "high"},
        {"quintile": 5, "language_group": "en", "item_id": "i1", "score": 1, "ability_group": "high"},
    ]
    report = evaluate_educational_fairness(records)
    assert report.quintile_parity_satisfied
    assert report.language_parity_satisfied
    assert len(report.quintile_subgroups) == 2


def test_mantel_haenszel_dif():
    records = [
        # Focal group (Q1)
        {"quintile": 1, "item_id": "item-A", "ability_group": "high", "score": 1},
        {"quintile": 1, "item_id": "item-A", "ability_group": "high", "score": 0},
        # Reference group (Q5)
        {"quintile": 5, "item_id": "item-A", "ability_group": "high", "score": 1},
        {"quintile": 5, "item_id": "item-A", "ability_group": "high", "score": 1},
    ]
    dif_results = compute_mantel_haenszel_dif(
        records,
        focal_predicate=lambda r: r["quintile"] == 1,
        reference_predicate=lambda r: r["quintile"] == 5,
    )
    assert len(dif_results) == 1
    assert dif_results[0].item_id == "item-A"
    assert dif_results[0].dif_class in ("A", "B", "C")


def test_analyze_interaction_safety_nominal():
    events = [
        {"response_latency_ms": 5000, "hint_count": 0, "attempt_count": 1, "first_attempt_correct": True},
        {"response_latency_ms": 6000, "hint_count": 0, "attempt_count": 1, "first_attempt_correct": True},
    ]
    status = analyze_interaction_safety("lrn-01", events)
    assert status.severity == SafetySeverity.NOMINAL
    assert not status.cognitive_overload_flag


def test_analyze_interaction_safety_critical_stop_work():
    events = [
        {"response_latency_ms": 800, "hint_count": 3, "attempt_count": 3, "first_attempt_correct": False},
        {"response_latency_ms": 700, "hint_count": 3, "attempt_count": 3, "first_attempt_correct": False},
        {"response_latency_ms": 600, "hint_count": 3, "attempt_count": 3, "first_attempt_correct": False},
    ]
    status = analyze_interaction_safety("lrn-01", events)
    assert status.severity == SafetySeverity.CRITICAL_STOP_WORK
    assert status.cognitive_overload_flag
    assert "HALT" in status.recommended_action
