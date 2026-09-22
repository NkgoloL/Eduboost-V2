"""Educational Model Drift Detection Service (LEV-WS13).

Calculates Population Stability Index (PSI), two-sample Kolmogorov-Smirnov (KS) tests,
Wasserstein distance, and item parameter drift to ensure pedagogical and psychometric
validity over time.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import math
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
from scipy import stats


class DriftLevel(str, Enum):
    STABLE = "stable"
    MODERATE_DRIFT = "moderate_drift"
    CRITICAL_DRIFT = "critical_drift"


@dataclass(frozen=True)
class BucketDetail:
    bucket_index: int
    lower_bound: float
    upper_bound: float
    expected_count: int
    actual_count: int
    expected_fraction: float
    actual_fraction: float
    psi_contribution: float


@dataclass(frozen=True)
class DriftMetrics:
    psi: float
    ks_statistic: float
    ks_pvalue: float
    wasserstein_distance: float
    drift_level: DriftLevel
    alert_required: bool
    sample_size_baseline: int
    sample_size_current: int
    buckets: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "psi": round(self.psi, 6),
            "ks_statistic": round(self.ks_statistic, 6),
            "ks_pvalue": round(self.ks_pvalue, 6),
            "wasserstein_distance": round(self.wasserstein_distance, 6),
            "drift_level": self.drift_level.value,
            "alert_required": self.alert_required,
            "sample_size_baseline": self.sample_size_baseline,
            "sample_size_current": self.sample_size_current,
            "buckets": self.buckets,
        }


def calculate_psi(
    baseline: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
    num_buckets: int = 10,
    epsilon: float = 1e-4,
) -> Tuple[float, List[BucketDetail]]:
    """Calculate Population Stability Index (PSI) between baseline and current distributions.

    Standard psychometric/data-science thresholds:
      PSI < 0.10: Stable / no shift
      0.10 <= PSI < 0.20: Moderate shift (re-calibration recommended)
      PSI >= 0.20: Significant shift (action required / halt automated decisions)
    """
    if len(baseline) == 0 or len(current) == 0:
        raise ValueError("Baseline and current datasets must not be empty.")

    b_arr = np.asarray(baseline, dtype=float)
    c_arr = np.asarray(current, dtype=float)

    # Bin edges based on baseline quantiles
    quantiles = np.linspace(0, 100, num_buckets + 1)
    bin_edges = np.percentile(b_arr, quantiles)
    # Ensure distinct bin edges
    bin_edges = np.unique(bin_edges)
    if len(bin_edges) < 2:
        bin_edges = np.linspace(min(b_arr.min(), c_arr.min()) - 1e-5, max(b_arr.max(), c_arr.max()) + 1e-5, num_buckets + 1)

    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    b_counts, _ = np.histogram(b_arr, bins=bin_edges)
    c_counts, _ = np.histogram(c_arr, bins=bin_edges)

    total_b = len(b_arr)
    total_c = len(c_arr)

    b_fracs = (b_counts + epsilon) / (total_b + epsilon * len(b_counts))
    c_fracs = (c_counts + epsilon) / (total_c + epsilon * len(c_counts))

    psi_total = 0.0
    bucket_details: List[BucketDetail] = []

    for idx in range(len(b_counts)):
        low = float(bin_edges[idx])
        high = float(bin_edges[idx + 1])
        e_frac = float(b_fracs[idx])
        a_frac = float(c_fracs[idx])
        sub_psi = (a_frac - e_frac) * math.log(a_frac / e_frac)
        psi_total += sub_psi

        bucket_details.append(
            BucketDetail(
                bucket_index=idx,
                lower_bound=low,
                upper_bound=high,
                expected_count=int(b_counts[idx]),
                actual_count=int(c_counts[idx]),
                expected_fraction=round(e_frac, 6),
                actual_fraction=round(a_frac, 6),
                psi_contribution=round(sub_psi, 6),
            )
        )

    return float(psi_total), bucket_details


def evaluate_model_drift(
    baseline: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
    psi_warning: float = 0.10,
    psi_critical: float = 0.20,
    ks_alpha: float = 0.05,
    num_buckets: int = 10,
) -> DriftMetrics:
    """Perform comprehensive drift evaluation including PSI, KS-test, and Wasserstein distance."""
    b_arr = np.asarray(baseline, dtype=float)
    c_arr = np.asarray(current, dtype=float)

    psi_val, bucket_objs = calculate_psi(b_arr, c_arr, num_buckets=num_buckets)
    ks_res = stats.ks_2samp(b_arr, c_arr)
    ks_stat = float(ks_res.statistic)
    ks_pval = float(ks_res.pvalue)

    w_dist = float(stats.wasserstein_distance(b_arr, c_arr))

    if psi_val >= psi_critical or (ks_pval < (ks_alpha / 10.0) and psi_val >= psi_warning):
        level = DriftLevel.CRITICAL_DRIFT
        alert = True
    elif psi_val >= psi_warning or ks_pval < ks_alpha:
        level = DriftLevel.MODERATE_DRIFT
        alert = False
    else:
        level = DriftLevel.STABLE
        alert = False

    return DriftMetrics(
        psi=psi_val,
        ks_statistic=ks_stat,
        ks_pvalue=ks_pval,
        wasserstein_distance=w_dist,
        drift_level=level,
        alert_required=alert,
        sample_size_baseline=len(b_arr),
        sample_size_current=len(c_arr),
        buckets=[asdict(b) for b in bucket_objs],
    )


def check_item_parameter_drift(
    baseline_params: Dict[str, float],
    current_params: Dict[str, float],
    drift_threshold: float = 0.30,
) -> Dict[str, Any]:
    """Identify item-level difficulty or discrimination parameter drift."""
    flagged: List[Dict[str, Any]] = []
    checked = 0

    for item_id, base_val in baseline_params.items():
        if item_id in current_params:
            checked += 1
            curr_val = current_params[item_id]
            diff = abs(curr_val - base_val)
            if diff >= drift_threshold:
                flagged.append({
                    "item_id": item_id,
                    "baseline_param": base_val,
                    "current_param": curr_val,
                    "absolute_drift": round(diff, 4),
                    "relative_drift": round(diff / (abs(base_val) + 1e-6), 4),
                })

    return {
        "items_checked": checked,
        "items_drifted_count": len(flagged),
        "drift_rate": round(len(flagged) / max(1, checked), 4),
        "flagged_items": flagged,
    }
