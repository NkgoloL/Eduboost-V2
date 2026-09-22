from typing import Any, cast

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


def test_evaluate_model_calibration_calibrated():
    probs = [0.1 * i for i in range(10)]
    outs = [0 if p < 0.5 else 1 for p in probs]
    matrix = [[0.8, 0.9, 0.85], [0.2, 0.1, 0.3], [0.5, 0.6, 0.55]]
    metrics = evaluate_model_calibration(probs, outs, item_scores_matrix=matrix, ece_tolerance=0.25)
    assert metrics.is_calibrated is True
    assert metrics.sample_size == 10
    d = metrics.to_dict()
    assert "ece" in d
    assert "brier_score" in d
    assert d["evidence_type"] == "synthetic_fixture"


def test_compute_ece_validation_errors():
    with pytest.raises(ValueError, match="must not be empty"):
        compute_ece([], [])
    with pytest.raises(ValueError, match="equal length"):
        compute_ece([0.5], [1, 0])


def test_compute_brier_score_validation_errors():
    with pytest.raises(ValueError, match="identical non-zero lengths"):
        compute_brier_score([], [])
    with pytest.raises(ValueError, match="identical non-zero lengths"):
        compute_brier_score([0.5], [1, 0])


def test_compute_cronbach_alpha_edge_cases():
    # 1D array raises ValueError
    with pytest.raises(ValueError, match="2-dimensional"):
        compute_cronbach_alpha(cast(Any, [1.0, 2.0, 3.0]))

    # Fewer than 2 items -> 1.0
    matrix_1_item = [[1.0], [2.0], [3.0]]
    assert compute_cronbach_alpha(matrix_1_item) == 1.0

    # Fewer than 2 learners -> 0.0
    matrix_1_learner = [[1.0, 2.0, 3.0]]
    assert compute_cronbach_alpha(matrix_1_learner) == 0.0

    # Constant scores -> zero total variance -> 0.0
    matrix_constant = [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]
    assert compute_cronbach_alpha(matrix_constant) == 0.0


def test_wilson_ci():
    ci = compute_wilson_ci(50, 100)
    assert ci.lower < 0.50 < ci.upper
    assert ci.lower > 0.35
    assert ci.upper < 0.65

    # total <= 0
    zero_ci = compute_wilson_ci(0, 0)
    assert zero_ci.lower == 0.0
    assert zero_ci.upper == 0.0
    assert "lower" in zero_ci.to_dict()


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
    d = risk.to_dict()
    assert "confusion_matrix" in d
    assert d["confusion_matrix"]["tp"] == 2

    # Validation errors
    with pytest.raises(ValueError, match="non-empty and of identical length"):
        evaluate_classification_risk([], [])
    with pytest.raises(ValueError, match="non-empty and of identical length"):
        evaluate_classification_risk([True], [True, False])

    # No scores provided -> fallback roc_auc 0.5
    no_score_risk = evaluate_classification_risk([True, False], [True, False], mastery_scores=None)
    assert no_score_risk.roc_auc == 0.5
