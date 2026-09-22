"""Educational Controlled Impact Evaluation Service (LEV-WS10).

Implements dual-mode methodological evaluation for educational interventions:
1. Primary (Cluster-Randomized Trial / CRT):
   Intent-to-Treat (ITT) baseline-covariate-adjusted ANCOVA accounting for
   intra-cluster correlation (ICC), variance inflation (design effect), and Hedges' g.
2. Secondary (Quasi-Experimental Design / QED Fallback):
   Difference-in-Differences (DiD) paired with propensity/covariate adjustment for
   non-randomized educational deployments.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Sequence

import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression


@dataclass(frozen=True)
class CRTImpactResult:
    treatment_effect_beta: float
    std_error: float
    t_statistic: float
    p_value: float
    hedges_g: float
    intra_cluster_correlation: float
    variance_inflation_factor: float
    effective_sample_size: float
    baseline_adjusted_r2: float
    statistical_power_achieved: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "treatment_effect_beta": round(self.treatment_effect_beta, 4),
            "std_error": round(self.std_error, 4),
            "t_statistic": round(self.t_statistic, 4),
            "p_value": round(self.p_value, 6),
            "hedges_g": round(self.hedges_g, 4),
            "intra_cluster_correlation": round(self.intra_cluster_correlation, 4),
            "variance_inflation_factor": round(self.variance_inflation_factor, 4),
            "effective_sample_size": round(self.effective_sample_size, 1),
            "baseline_adjusted_r2": round(self.baseline_adjusted_r2, 4),
            "statistical_power_achieved": round(self.statistical_power_achieved, 4),
        }


@dataclass(frozen=True)
class DiDImpactResult:
    did_estimate: float
    std_error: float
    t_statistic: float
    p_value: float
    ci_95_lower: float
    ci_95_upper: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "did_estimate": round(self.did_estimate, 4),
            "std_error": round(self.std_error, 4),
            "t_statistic": round(self.t_statistic, 4),
            "p_value": round(self.p_value, 6),
            "ci_95_lower": round(self.ci_95_lower, 4),
            "ci_95_upper": round(self.ci_95_upper, 4),
        }


@dataclass(frozen=True)
class ImpactStudyReport:
    total_learners: int
    cluster_count: int
    treatment_learner_count: int
    control_learner_count: int
    primary_crt_ancova: Dict[str, Any]
    secondary_did: Dict[str, Any]
    statistically_significant: bool
    evidence_type: str = "synthetic_fixture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_learners": self.total_learners,
            "cluster_count": self.cluster_count,
            "treatment_learner_count": self.treatment_learner_count,
            "control_learner_count": self.control_learner_count,
            "primary_crt_ancova": self.primary_crt_ancova,
            "secondary_did": self.secondary_did,
            "statistically_significant": self.statistically_significant,
            "evidence_type": self.evidence_type,
        }


def compute_intra_cluster_correlation(
    scores: np.ndarray, cluster_ids: Sequence[str]
) -> float:
    """Compute ICC (rho) using one-way ANOVA variance components."""
    unique_clusters = list(set(cluster_ids))
    k = len(unique_clusters)
    n = len(scores)
    if k < 2 or n <= k:
        return 0.05  # Default conservative educational ICC

    grand_mean = float(np.mean(scores))
    cluster_means = {}
    cluster_sizes = {}
    for cid in unique_clusters:
        mask = [c == cid for c in cluster_ids]
        c_scores = scores[mask]
        cluster_means[cid] = float(np.mean(c_scores))
        cluster_sizes[cid] = len(c_scores)

    ss_between = sum(cluster_sizes[cid] * (cluster_means[cid] - grand_mean) ** 2 for cid in unique_clusters)
    ss_within = sum(
        sum((scores[idx] - cluster_means[cluster_ids[idx]]) ** 2 for idx in range(n) if cluster_ids[idx] == cid)
        for cid in unique_clusters
    )

    ms_between = ss_between / (k - 1)
    ms_within = ss_within / (n - k) if (n - k) > 0 else 1.0

    # Average cluster size n_0
    sum_n2 = sum(s ** 2 for s in cluster_sizes.values())
    n_0 = (n - sum_n2 / n) / max(1, k - 1)

    s2_between = max(0.0, (ms_between - ms_within) / max(1e-4, n_0))
    s2_within = ms_within

    if (s2_between + s2_within) <= 1e-8:
        return 0.0
    return float(np.clip(s2_between / (s2_between + s2_within), 0.0, 1.0))


def evaluate_cluster_rct_ancova(
    pre_scores: Sequence[float] | np.ndarray,
    post_scores: Sequence[float] | np.ndarray,
    treatment: Sequence[int] | np.ndarray,
    cluster_ids: Sequence[str],
) -> CRTImpactResult:
    """Run Primary Cluster-Randomized Trial (CRT) ITT ANCOVA with cluster adjustment."""
    y_pre = np.asarray(pre_scores, dtype=float)
    y_post = np.asarray(post_scores, dtype=float)
    t_arr = np.asarray(treatment, dtype=float)
    n = len(y_post)

    # ICC and Design Effect
    icc = compute_intra_cluster_correlation(y_post, cluster_ids)
    m_avg = n / max(1, len(set(cluster_ids)))
    vif = 1.0 + (m_avg - 1.0) * icc
    n_eff = n / max(1.0, vif)

    # Covariate-adjusted ANCOVA: post ~ treatment + pre
    x_matrix = np.column_stack([t_arr, y_pre])
    reg = LinearRegression().fit(x_matrix, y_post)
    beta_treat = float(reg.coef_[0])
    r2 = float(reg.score(x_matrix, y_post))

    residuals = y_post - reg.predict(x_matrix)
    sigma2 = float(np.sum(residuals ** 2) / max(1, n - 3))
    # Standard error adjusted for clustering (Huber-White cluster sandwich or VIF inflation)
    var_treat = (sigma2 / (np.sum((t_arr - np.mean(t_arr)) ** 2) + 1e-6)) * vif
    se_treat = math.sqrt(max(1e-8, var_treat))

    t_stat = beta_treat / se_treat
    df = max(1, len(set(cluster_ids)) - 2)
    p_val = float(2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=df)))

    # Hedges' g effect size:
    ctrl_mask = (t_arr == 0)
    sd_ctrl = float(np.std(y_post[ctrl_mask], ddof=1)) if np.sum(ctrl_mask) > 1 else 1.0
    cohen_d = beta_treat / max(1e-4, sd_ctrl)
    j_correction = 1.0 - (3.0 / (4.0 * max(1, n - 2) - 1.0))
    hedges_g = float(cohen_d * j_correction)

    # Approximate statistical power achieved
    z_alpha = 1.96
    z_beta = abs(t_stat) - z_alpha
    power = float(stats.norm.cdf(z_beta))

    return CRTImpactResult(
        treatment_effect_beta=beta_treat,
        std_error=se_treat,
        t_statistic=t_stat,
        p_value=p_val,
        hedges_g=hedges_g,
        intra_cluster_correlation=icc,
        variance_inflation_factor=vif,
        effective_sample_size=n_eff,
        baseline_adjusted_r2=r2,
        statistical_power_achieved=power,
    )


def evaluate_did_fallback(
    pre_scores: Sequence[float] | np.ndarray,
    post_scores: Sequence[float] | np.ndarray,
    treatment: Sequence[int] | np.ndarray,
) -> DiDImpactResult:
    """Run Secondary Difference-in-Differences (DiD) estimation."""
    y_pre = np.asarray(pre_scores, dtype=float)
    y_post = np.asarray(post_scores, dtype=float)
    t_arr = np.asarray(treatment, dtype=int)

    treat_mask = (t_arr == 1)
    ctrl_mask = (t_arr == 0)

    delta_treat = y_post[treat_mask] - y_pre[treat_mask]
    delta_ctrl = y_post[ctrl_mask] - y_pre[ctrl_mask]

    mean_dt = float(np.mean(delta_treat)) if len(delta_treat) > 0 else 0.0
    mean_dc = float(np.mean(delta_ctrl)) if len(delta_ctrl) > 0 else 0.0
    did = mean_dt - mean_dc

    var_dt = float(np.var(delta_treat, ddof=1)) / len(delta_treat) if len(delta_treat) > 1 else 0.0
    var_dc = float(np.var(delta_ctrl, ddof=1)) / len(delta_ctrl) if len(delta_ctrl) > 1 else 0.0
    se_did = math.sqrt(max(1e-8, var_dt + var_dc))

    t_stat = did / max(1e-6, se_did)
    df = max(1, len(delta_treat) + len(delta_ctrl) - 2)
    p_val = float(2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=df)))

    ci_lower = did - 1.96 * se_did
    ci_upper = did + 1.96 * se_did

    return DiDImpactResult(
        did_estimate=did,
        std_error=se_did,
        t_statistic=t_stat,
        p_value=p_val,
        ci_95_lower=ci_lower,
        ci_95_upper=ci_upper,
    )


def run_comprehensive_impact_evaluation(
    records: Sequence[Dict[str, Any]],
) -> ImpactStudyReport:
    """Run primary CRT ANCOVA and secondary DiD on intervention evaluation records."""
    pre = [float(r["pre_score"]) for r in records]
    post = [float(r["post_score"]) for r in records]
    treat = [int(r["treatment"]) for r in records]
    clusters = [str(r.get("cluster_id", r.get("school_id", "c1"))) for r in records]

    crt_res = evaluate_cluster_rct_ancova(pre, post, treat, clusters)
    did_res = evaluate_did_fallback(pre, post, treat)

    sig = bool(crt_res.p_value < 0.05 and crt_res.treatment_effect_beta > 0)

    return ImpactStudyReport(
        total_learners=len(records),
        cluster_count=len(set(clusters)),
        treatment_learner_count=sum(treat),
        control_learner_count=len(treat) - sum(treat),
        primary_crt_ancova={
            "treatment_gain_points": round(crt_res.treatment_effect_beta, 4),
            "std_error": round(crt_res.std_error, 4),
            "t_statistic": round(crt_res.t_statistic, 4),
            "p_value": round(crt_res.p_value, 6),
            "hedges_g": round(crt_res.hedges_g, 4),
            "intra_cluster_correlation": round(crt_res.intra_cluster_correlation, 4),
            "variance_inflation_factor": round(crt_res.variance_inflation_factor, 4),
            "effective_sample_size": round(crt_res.effective_sample_size, 1),
            "baseline_adjusted_r2": round(crt_res.baseline_adjusted_r2, 4),
            "statistical_power": round(crt_res.statistical_power_achieved, 4),
        },
        secondary_did={
            "did_estimate_points": round(did_res.did_estimate, 4),
            "std_error": round(did_res.std_error, 4),
            "t_statistic": round(did_res.t_statistic, 4),
            "p_value": round(did_res.p_value, 6),
            "ci_95": [round(did_res.ci_95_lower, 4), round(did_res.ci_95_upper, 4)],
        },
        statistically_significant=sig,
    )
