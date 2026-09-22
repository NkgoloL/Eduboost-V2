import numpy as np
import pytest

from app.services.educational_validation.impact import (
    compute_intra_cluster_correlation,
    evaluate_cluster_rct_ancova,
    evaluate_did_fallback,
    run_comprehensive_impact_evaluation,
)
from app.services.educational_validation.retention import fit_multi_model_retention


def test_fit_multi_model_retention():
    # Synthetic decaying retention data across 14, 30, 60, 90 days
    days = [14] * 25 + [30] * 25 + [60] * 25 + [90] * 25
    # True exponential decay with half life ~ 35
    np.random.seed(42)
    scores = [float(np.clip(np.exp(-d / 35.0) + np.random.normal(0, 0.05), 0, 1)) for d in days]

    report = fit_multi_model_retention(days, scores)
    assert report.sample_size == 100
    assert len(report.interval_days) == 4
    assert report.best_model_name in ("exponential_decay", "power_law_decay", "two_component_decay")
    assert len(report.ranked_models) == 3


def test_compute_icc():
    scores = np.array([10.0, 11.0, 10.5, 20.0, 21.0, 20.5])
    clusters = ["c1", "c1", "c1", "c2", "c2", "c2"]
    icc = compute_intra_cluster_correlation(scores, clusters)
    # High between-cluster variance
    assert icc > 0.50


def test_evaluate_cluster_rct_ancova():
    np.random.seed(42)
    n = 100
    pre = np.random.normal(50, 5, n)
    # Half treatment, half control
    treat = [1 if i < 50 else 0 for i in range(n)]
    clusters = [f"school_{i % 10}" for i in range(n)]
    post = [p + (8.0 if t == 1 else 1.0) + np.random.normal(0, 2) for p, t in zip(pre, treat)]

    res = evaluate_cluster_rct_ancova(pre, post, treat, clusters)
    assert res.treatment_effect_beta > 5.0
    assert res.t_statistic > 2.0
    assert res.hedges_g > 0.3


def test_evaluate_did_fallback():
    pre = [40.0, 42.0, 50.0, 52.0]
    post = [55.0, 57.0, 51.0, 53.0]
    # Treatment gained 15, control gained 1 -> DiD = 14
    treat = [1, 1, 0, 0]
    did_res = evaluate_did_fallback(pre, post, treat)
    assert did_res.did_estimate == pytest.approx(14.0)
    assert did_res.t_statistic > 2.0


def test_run_comprehensive_impact_evaluation():
    records = [
        {"learner_pseudonym": f"l_{i}", "pre_score": 50.0, "post_score": 60.0 if i < 10 else 52.0, "treatment": 1 if i < 10 else 0, "cluster_id": f"c_{i%4}"}
        for i in range(20)
    ]
    rep = run_comprehensive_impact_evaluation(records)
    assert rep.total_learners == 20
    assert rep.cluster_count == 4
    assert rep.treatment_learner_count == 10
    d = rep.to_dict()
    assert "primary_crt_ancova" in d
    assert "secondary_did" in d
    assert d["evidence_type"] == "synthetic_fixture"


def test_fit_multi_model_retention_validation_errors():
    with pytest.raises(ValueError, match="At least 4 paired retention observations"):
        fit_multi_model_retention([14, 30], [0.8, 0.6])
    with pytest.raises(ValueError, match="At least 4 paired retention observations"):
        fit_multi_model_retention([14, 30, 60, 90], [0.8, 0.6, 0.4])


def test_retention_report_to_dict():
    days = [14, 30, 60, 90] * 5
    scores = [0.8, 0.6, 0.4, 0.2] * 5
    rep = fit_multi_model_retention(days, scores)
    d = rep.to_dict()
    assert "best_model_name" in d
    assert "mean_retention_by_interval" in d
    assert d["evidence_type"] == "synthetic_fixture"


def test_compute_icc_edge_cases():
    # Single cluster -> returns default conservative ICC (0.05)
    scores = np.array([10.0, 11.0, 12.0])
    clusters = ["c1", "c1", "c1"]
    assert compute_intra_cluster_correlation(scores, clusters) == 0.05

    # Zero total variance -> 0.0
    scores_const = np.array([10.0, 10.0, 10.0, 10.0])
    clusters_2 = ["c1", "c1", "c2", "c2"]
    assert compute_intra_cluster_correlation(scores_const, clusters_2) == 0.0


def test_evaluate_did_fallback_edge_cases():
    # Single observation per group
    pre = [40.0, 50.0]
    post = [50.0, 51.0]
    treat = [1, 0]
    did_res = evaluate_did_fallback(pre, post, treat)
    assert did_res.did_estimate == pytest.approx(9.0)
    assert did_res.std_error >= 0.0
    d = did_res.to_dict()
    assert "did_estimate" in d
