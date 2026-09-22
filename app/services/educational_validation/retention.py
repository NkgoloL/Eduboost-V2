"""Educational Spaced Retention & Multi-Model Decay Fitting Engine (LEV-WS06).

Fits three competing functional forms of memory decay across spaced intervals (14d, 30d, 60d, 90d):
1. Exponential Decay (Ebbinghaus): R(t) = exp(-t / S)
2. Power-Law Decay (Wixted & Ebbesen): R(t) = (1 + alpha * t)^(-beta)
3. Two-Component Half-Life Model (Pavlik & Anderson): R(t) = w * exp(-t / S1) + (1 - w) * exp(-t / S2)

Ranks candidate models empirically by AIC, BIC, and RMSE to determine best fit.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, List, Sequence

import numpy as np
from scipy.optimize import curve_fit


@dataclass(frozen=True)
class ModelFitResult:
    model_name: str
    parameters: Dict[str, float]
    rmse: float
    aic: float
    bic: float
    converged: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "parameters": {k: round(v, 4) for k, v in self.parameters.items()},
            "rmse": round(self.rmse, 4),
            "aic": round(self.aic, 4),
            "bic": round(self.bic, 4),
            "converged": self.converged,
        }


@dataclass(frozen=True)
class RetentionAnalysisReport:
    best_model_name: str
    sample_size: int
    interval_days: List[int]
    mean_retention_by_interval: Dict[int, float]
    ranked_models: List[Dict[str, Any]]
    evidence_type: str = "synthetic_fixture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "best_model_name": self.best_model_name,
            "sample_size": self.sample_size,
            "interval_days": self.interval_days,
            "mean_retention_by_interval": {
                str(k): round(v, 4) for k, v in self.mean_retention_by_interval.items()
            },
            "ranked_models": self.ranked_models,
            "evidence_type": self.evidence_type,
        }


def _exponential_decay(t: np.ndarray, s: float) -> np.ndarray:
    return np.exp(-t / np.maximum(1e-4, s))


def _power_law_decay(t: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    return (1.0 + np.maximum(0.0, alpha) * t) ** (-np.maximum(1e-4, beta))


def _two_component_decay(t: np.ndarray, w: float, s1: float, s2: float) -> np.ndarray:
    w_clamped = np.clip(w, 0.0, 1.0)
    return w_clamped * np.exp(-t / np.maximum(1e-4, s1)) + (1.0 - w_clamped) * np.exp(-t / np.maximum(1e-4, s2))


def fit_multi_model_retention(
    days: Sequence[int],
    retention_scores: Sequence[float],
) -> RetentionAnalysisReport:
    """Fit exponential, power-law, and two-component retention decay models and rank by AIC/BIC."""
    if len(days) < 4 or len(days) != len(retention_scores):
        raise ValueError("At least 4 paired retention observations required.")

    t_arr = np.asarray(days, dtype=float)
    y_arr = np.asarray(retention_scores, dtype=float)
    n = len(t_arr)

    # Compute mean retention across distinct intervals
    unique_intervals = sorted(set(int(d) for d in t_arr))
    means_by_interval: Dict[int, float] = {}
    for d in unique_intervals:
        mask = (t_arr == d)
        means_by_interval[d] = float(np.mean(y_arr[mask]))

    candidates: List[ModelFitResult] = []

    # 1. Exponential Decay (k = 1 parameter)
    try:
        popt, _ = curve_fit(_exponential_decay, t_arr, y_arr, p0=[30.0], bounds=(1.0, 365.0), maxfev=2000)
        y_pred = _exponential_decay(t_arr, *popt)
        rss = float(np.sum((y_arr - y_pred) ** 2))
        rmse = math.sqrt(rss / n)
        k = 1
        aic = n * math.log(max(1e-12, rss / n)) + 2 * k
        bic = n * math.log(max(1e-12, rss / n)) + k * math.log(n)
        candidates.append(
            ModelFitResult(
                model_name="exponential_decay",
                parameters={"half_life_days": float(popt[0])},
                rmse=rmse,
                aic=aic,
                bic=bic,
                converged=True,
            )
        )
    except Exception:
        candidates.append(
            ModelFitResult(
                model_name="exponential_decay",
                parameters={},
                rmse=999.0,
                aic=9999.0,
                bic=9999.0,
                converged=False,
            )
        )

    # 2. Power-Law Decay (k = 2 parameters)
    try:
        popt, _ = curve_fit(_power_law_decay, t_arr, y_arr, p0=[0.05, 0.5], bounds=([1e-4, 1e-4], [5.0, 5.0]), maxfev=2000)
        y_pred = _power_law_decay(t_arr, *popt)
        rss = float(np.sum((y_arr - y_pred) ** 2))
        rmse = math.sqrt(rss / n)
        k = 2
        aic = n * math.log(max(1e-12, rss / n)) + 2 * k
        bic = n * math.log(max(1e-12, rss / n)) + k * math.log(n)
        candidates.append(
            ModelFitResult(
                model_name="power_law_decay",
                parameters={"alpha": float(popt[0]), "beta": float(popt[1])},
                rmse=rmse,
                aic=aic,
                bic=bic,
                converged=True,
            )
        )
    except Exception:
        candidates.append(
            ModelFitResult(
                model_name="power_law_decay",
                parameters={},
                rmse=999.0,
                aic=9999.0,
                bic=9999.0,
                converged=False,
            )
        )

    # 3. Two-Component Decay (k = 3 parameters)
    try:
        popt, _ = curve_fit(
            _two_component_decay,
            t_arr,
            y_arr,
            p0=[0.5, 10.0, 60.0],
            bounds=([0.0, 1.0, 10.0], [1.0, 30.0, 365.0]),
            maxfev=2000,
        )
        y_pred = _two_component_decay(t_arr, *popt)
        rss = float(np.sum((y_arr - y_pred) ** 2))
        rmse = math.sqrt(rss / n)
        k = 3
        aic = n * math.log(max(1e-12, rss / n)) + 2 * k
        bic = n * math.log(max(1e-12, rss / n)) + k * math.log(n)
        candidates.append(
            ModelFitResult(
                model_name="two_component_decay",
                parameters={"weight_fast": float(popt[0]), "s1_fast_days": float(popt[1]), "s2_slow_days": float(popt[2])},
                rmse=rmse,
                aic=aic,
                bic=bic,
                converged=True,
            )
        )
    except Exception:
        candidates.append(
            ModelFitResult(
                model_name="two_component_decay",
                parameters={},
                rmse=999.0,
                aic=9999.0,
                bic=9999.0,
                converged=False,
            )
        )

    # Rank by AIC ascending
    ranked = sorted(candidates, key=lambda m: (not m.converged, m.aic))
    best = ranked[0].model_name

    return RetentionAnalysisReport(
        best_model_name=best,
        sample_size=n,
        interval_days=unique_intervals,
        mean_retention_by_interval=means_by_interval,
        ranked_models=[m.to_dict() for m in ranked],
    )
