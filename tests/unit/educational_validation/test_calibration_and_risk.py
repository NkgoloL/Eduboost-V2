import numpy as np
import pytest

from app.services.educational_validation.calibration import (
    compute_brier_score,
    compute_cronbach_alpha,
    compute_ece,
    evaluate_model_calibration,
)
from app.services.educational_validation.classification import (
    compute_wilson_ci,
    evaluate_classification_risk,
)


def test_compute_ece_perfect():
    probs = [0.1, 0.1, 0.9, 0.9]
    outs = [0, 0, 1, 1]
    ece, mce, bins = compute_ece(probs, outs, num_bins=10)
    assert ece == pytest.approx(0.1, abs=0.05)
    assert len(bins) == 10


def test_compute_brier_score():
    probs = [0.8, 0.2]
    outs = [1, 0]
    brier = compute_brier_score(probs, outs)
    assert brier == pytest.approx((0.2**2 + 0.2**2) / 2.0)


def test_compute_cronbach_alpha():
    # 10 learners, 4 items with high positive correlation
    np.random.seed(42)
    base = np.random.normal(0, 1, 50)
    matrix = np.column_stack([base + np.random.normal(0, 0.2, 50) for _ in range(4)])
    alpha = compute_cronbach_alpha(matrix)
    assert alpha > 0.80


def test_wilson_ci():
    ci = compute_wilson_ci(50, 100)
    assert ci.lower < 0.50 < ci.upper
    assert ci.lower > 0.35
    assert ci.upper < 0.65


def test_evaluate_classification_risk():
    pred = [True, True, False, False, True]
    true_m = [True, False, False, True, True]
    scores = [0.9, 0.7, 0.2, 0.4, 0.85]
    risk = evaluate_classification_risk(pred, true_m, scores)
    assert risk.true_positives == 2
    assert risk.false_positives == 1
    assert risk.true_negatives == 1
    assert risk.false_negatives == 1
    assert risk.asymmetric_educational_loss > 0.0
    assert 0.0 <= risk.roc_auc <= 1.0
