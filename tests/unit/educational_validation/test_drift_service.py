import numpy as np
import pytest

from app.services.educational_validation.drift import (
    DriftLevel,
    calculate_psi,
    check_item_parameter_drift,
    evaluate_model_drift,
)


def test_psi_identical_distributions():
    np.random.seed(42)
    data = np.random.normal(0.5, 0.1, 1000)
    psi, buckets = calculate_psi(data, data, num_buckets=10)
    assert psi < 0.05
    assert len(buckets) == 10


def test_psi_shifted_distribution():
    np.random.seed(42)
    baseline = np.random.normal(0.5, 0.1, 1000)
    current = np.random.normal(0.8, 0.1, 1000)
    psi, buckets = calculate_psi(baseline, current, num_buckets=10)
    assert psi > 0.20


def test_evaluate_model_drift_stable():
    np.random.seed(42)
    baseline = np.random.normal(0.6, 0.1, 500)
    current = np.random.normal(0.605, 0.1, 500)
    result = evaluate_model_drift(baseline, current)
    assert result.drift_level in (DriftLevel.STABLE, DriftLevel.MODERATE_DRIFT)
    assert not result.alert_required
    assert result.sample_size_baseline == 500
    assert result.sample_size_current == 500


def test_evaluate_model_drift_critical():
    np.random.seed(42)
    baseline = np.random.normal(0.4, 0.1, 500)
    current = np.random.normal(0.8, 0.1, 500)
    result = evaluate_model_drift(baseline, current)
    assert result.drift_level == DriftLevel.CRITICAL_DRIFT
    assert result.alert_required


def test_check_item_parameter_drift():
    baseline = {"item_1": 0.5, "item_2": -0.2, "item_3": 1.2}
    current = {"item_1": 0.52, "item_2": 0.35, "item_3": 1.25}  # item_2 drifted by 0.55 > 0.30
    drift_report = check_item_parameter_drift(baseline, current, drift_threshold=0.30)
    assert drift_report["items_checked"] == 3
    assert drift_report["items_drifted_count"] == 1
    assert drift_report["flagged_items"][0]["item_id"] == "item_2"


def test_drift_metrics_to_dict_and_edge_cases():
    with pytest.raises(ValueError, match="must not be empty"):
        calculate_psi([], [1.0])
    with pytest.raises(ValueError, match="must not be empty"):
        calculate_psi([1.0], [])

    # Constant baseline -> unique edges < 2 branch
    psi, buckets = calculate_psi([0.5, 0.5, 0.5, 0.5], [0.5, 0.5, 0.5, 0.5])
    assert psi == pytest.approx(0.0, abs=1e-3)

    # Moderate drift
    np.random.seed(42)
    b = np.random.normal(0.5, 0.1, 500)
    c = np.random.normal(0.54, 0.1, 500)
    res = evaluate_model_drift(b, c, psi_warning=0.01, psi_critical=0.50)
    assert res.drift_level in (DriftLevel.MODERATE_DRIFT, DriftLevel.CRITICAL_DRIFT)

    d = res.to_dict()
    assert "psi" in d
    assert "ks_statistic" in d
    assert "drift_level" in d
