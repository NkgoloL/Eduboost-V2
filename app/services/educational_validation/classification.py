"""Educational Classification & False-Mastery Risk Service (LEV-WS05).

Estimates false-mastery rates (FMR), false-non-mastery rates (FNMR), Wilson score
confidence intervals, ROC-AUC, and asymmetric educational risk cost models.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Sequence

import numpy as np
from scipy import stats
from sklearn import metrics as sk_metrics


@dataclass(frozen=True)
class ConfidenceInterval:
    lower: float
    upper: float
    confidence_level: float = 0.95

    def to_dict(self) -> Dict[str, float]:
        return {
            "lower": round(self.lower, 4),
            "upper": round(self.upper, 4),
            "confidence_level": self.confidence_level,
        }


@dataclass(frozen=True)
class ClassificationRiskMetrics:
    total_samples: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    false_mastery_rate: float
    fmr_ci_95: ConfidenceInterval
    false_non_mastery_rate: float
    fnmr_ci_95: ConfidenceInterval
    precision: float
    recall: float
    roc_auc: float
    asymmetric_educational_loss: float
    evidence_type: str = "synthetic_fixture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_samples": self.total_samples,
            "confusion_matrix": {
                "tp": self.true_positives,
                "fp": self.false_positives,
                "tn": self.true_negatives,
                "fn": self.false_negatives,
            },
            "false_mastery_rate": round(self.false_mastery_rate, 4),
            "fmr_ci_95": self.fmr_ci_95.to_dict(),
            "false_non_mastery_rate": round(self.false_non_mastery_rate, 4),
            "fnmr_ci_95": self.fnmr_ci_95.to_dict(),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "roc_auc": round(self.roc_auc, 4),
            "asymmetric_educational_loss": round(self.asymmetric_educational_loss, 4),
            "evidence_type": self.evidence_type,
        }


def compute_wilson_ci(
    successes: int,
    total: int,
    confidence: float = 0.95,
) -> ConfidenceInterval:
    """Compute Wilson score interval for binomial proportion."""
    if total <= 0:
        return ConfidenceInterval(lower=0.0, upper=0.0, confidence_level=confidence)

    z = float(stats.norm.ppf(1.0 - (1.0 - confidence) / 2.0))
    p = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    half_width = (z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total)) / denominator

    lower = max(0.0, center - half_width)
    upper = min(1.0, center + half_width)
    return ConfidenceInterval(lower=lower, upper=upper, confidence_level=confidence)


def evaluate_classification_risk(
    predicted_mastery: Sequence[bool] | Sequence[float] | np.ndarray,
    true_mastery: Sequence[bool] | Sequence[float] | np.ndarray,
    mastery_scores: Sequence[float] | np.ndarray | None = None,
    cost_false_mastery: float = 5.0,
    cost_false_non_mastery: float = 1.0,
) -> ClassificationRiskMetrics:
    """Evaluate classification confusion, risk bounds, and educational loss."""
    if len(predicted_mastery) != len(true_mastery) or len(predicted_mastery) == 0:
        raise ValueError("Predicted and true mastery sequences must be non-empty and of identical length.")

    n = len(predicted_mastery)
    tp = sum(1 for p, t in zip(predicted_mastery, true_mastery, strict=False) if p and t)
    fp = sum(1 for p, t in zip(predicted_mastery, true_mastery, strict=False) if p and not t)
    tn = sum(1 for p, t in zip(predicted_mastery, true_mastery, strict=False) if not p and not t)
    fn = sum(1 for p, t in zip(predicted_mastery, true_mastery, strict=False) if not p and t)

    # FMR = FP / (TN + FP) [False Positive Rate / False Mastery Rate]
    actual_negatives = tn + fp
    fmr = (fp / actual_negatives) if actual_negatives > 0 else 0.0
    fmr_ci = compute_wilson_ci(fp, actual_negatives)

    # FNMR = FN / (TP + FN) [False Negative Rate / False Non-Mastery Rate]
    actual_positives = tp + fn
    fnmr = (fn / actual_positives) if actual_positives > 0 else 0.0
    fnmr_ci = compute_wilson_ci(fn, actual_positives)

    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = (tp / actual_positives) if actual_positives > 0 else 0.0

    # ROC-AUC
    auc = 0.5
    if mastery_scores is not None and len(mastery_scores) == n:
        try:
            auc = float(sk_metrics.roc_auc_score([1 if t else 0 for t in true_mastery], mastery_scores))
        except Exception:
            auc = 0.5

    # Asymmetric loss: Cost(FP) * FP + Cost(FN) * FN normalized by N
    loss = (cost_false_mastery * fp + cost_false_non_mastery * fn) / float(n)

    return ClassificationRiskMetrics(
        total_samples=n,
        true_positives=tp,
        false_positives=fp,
        true_negatives=tn,
        false_negatives=fn,
        false_mastery_rate=fmr,
        fmr_ci_95=fmr_ci,
        false_non_mastery_rate=fnmr,
        fnmr_ci_95=fnmr_ci,
        precision=precision,
        recall=recall,
        roc_auc=auc,
        asymmetric_educational_loss=loss,
    )
