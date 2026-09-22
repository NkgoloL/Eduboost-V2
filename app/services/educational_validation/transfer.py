"""Educational Transfer Validity Service (LEV-WS07).

Evaluates near transfer, far transfer, and detects unsupported extrapolations.
Measures correlation between mastery of source concepts and novel/transfer item performance,
calculates transfer efficiency ratios, and flags unsupported cross-domain inferences.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy import stats


class TransferType(str, Enum):
    NEAR = "near"
    FAR = "far"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class TransferEvaluationResult:
    transfer_type: TransferType
    source_concept_id: str
    target_concept_id: str
    sample_size: int
    pearson_r: float
    pearson_pvalue: float
    spearman_rho: float
    spearman_pvalue: float
    transfer_efficiency_ratio: float
    is_transfer_valid: bool
    unsupported_warning: Optional[str] = None
    evidence_type: str = "synthetic_fixture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transfer_type": self.transfer_type.value,
            "source_concept_id": self.source_concept_id,
            "target_concept_id": self.target_concept_id,
            "sample_size": self.sample_size,
            "pearson_r": round(self.pearson_r, 4),
            "pearson_pvalue": round(self.pearson_pvalue, 6),
            "spearman_rho": round(self.spearman_rho, 4),
            "spearman_pvalue": round(self.spearman_pvalue, 6),
            "transfer_efficiency_ratio": round(self.transfer_efficiency_ratio, 4),
            "is_transfer_valid": self.is_transfer_valid,
            "unsupported_warning": self.unsupported_warning,
            "evidence_type": self.evidence_type,
        }


def evaluate_transfer_validity(
    source_scores: Sequence[float],
    target_scores: Sequence[float],
    source_concept_id: str,
    target_concept_id: str,
    transfer_type: TransferType = TransferType.NEAR,
    min_correlation: float = 0.30,
) -> TransferEvaluationResult:
    """Analyze the statistical relationship between source mastery and transfer performance."""
    if len(source_scores) < 5 or len(target_scores) < 5:
        raise ValueError("At least 5 paired observations required for transfer evaluation.")
    if len(source_scores) != len(target_scores):
        raise ValueError("Source and target scores must have matching lengths.")

    src = np.asarray(source_scores, dtype=float)
    tgt = np.asarray(target_scores, dtype=float)

    # Pearson correlation
    p_corr, p_val = stats.pearsonr(src, tgt)
    # Spearman rank correlation
    s_corr, s_val = stats.spearmanr(src, tgt)

    # Transfer efficiency: mean target score / mean source score
    mean_src = max(1e-4, float(np.mean(src)))
    mean_tgt = float(np.mean(tgt))
    transfer_ratio = mean_tgt / mean_src

    # Validity rules:
    # Near transfer requires r >= min_correlation (default 0.30)
    # Far transfer requires r >= min_correlation * 0.75
    threshold = min_correlation if transfer_type == TransferType.NEAR else (min_correlation * 0.70)
    is_valid = bool(p_corr >= threshold and p_val < 0.05)

    warning = None
    if not is_valid:
        warning = (
            f"Transfer from '{source_concept_id}' to '{target_concept_id}' ({transfer_type.value}) "
            f"failed validity threshold: Pearson r={p_corr:.3f} (p={p_val:.4f}). "
            f"System must not infer automated transfer mastery across this boundary."
        )

    return TransferEvaluationResult(
        transfer_type=transfer_type,
        source_concept_id=source_concept_id,
        target_concept_id=target_concept_id,
        sample_size=len(src),
        pearson_r=float(p_corr),
        pearson_pvalue=float(p_val),
        spearman_rho=float(s_corr),
        spearman_pvalue=float(s_val),
        transfer_efficiency_ratio=float(transfer_ratio),
        is_transfer_valid=is_valid,
        unsupported_warning=warning,
    )


def compute_transfer_matrix(
    transfer_records: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compute transfer evaluation across all concept pairs from transfer records."""
    grouped: Dict[Tuple[str, str, str], Dict[str, List[float]]] = {}

    for rec in transfer_records:
        src = rec["source_concept_id"]
        tgt = rec["target_concept_id"]
        ttype = rec.get("transfer_type", "near")
        key = (src, tgt, ttype)
        if key not in grouped:
            grouped[key] = {"source": [], "target": []}
        grouped[key]["source"].append(float(rec["source_score"]))
        grouped[key]["target"].append(float(rec["target_score"]))

    evaluations: List[Dict[str, Any]] = []
    for (src, tgt, ttype_str), scores in grouped.items():
        ttype = TransferType(ttype_str) if ttype_str in ("near", "far") else TransferType.UNSUPPORTED
        res = evaluate_transfer_validity(
            source_scores=scores["source"],
            target_scores=scores["target"],
            source_concept_id=src,
            target_concept_id=tgt,
            transfer_type=ttype,
        )
        evaluations.append(res.to_dict())

    valid_count = sum(1 for e in evaluations if e["is_transfer_valid"])
    return {
        "evidence_type": "synthetic_fixture",
        "total_pairs_evaluated": len(evaluations),
        "valid_transfer_pairs_count": valid_count,
        "transfer_evaluations": evaluations,
    }
