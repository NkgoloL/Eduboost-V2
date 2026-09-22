"""Educational Context & Fairness Validity Service (LEV-WS09).

Evaluates demographic parity and disparate impact calibrated to South African educational
contexts: DBE Quintile equity bands (Quintiles 1-3 no-fee vs Quintiles 4-5) and
official language groups (English, Afrikaans, isiXhosa).
Implements Mantel-Haenszel Differential Item Functioning (DIF) analysis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class SubgroupMetric:
    group_name: str
    sample_size: int
    pass_count: int
    pass_rate: float


@dataclass(frozen=True)
class DIFItemResult:
    item_id: str
    odds_ratio: float
    delta_mh: float
    dif_class: str  # "A" (negligible), "B" (moderate), "C" (severe)
    focal_group: str
    reference_group: str


@dataclass(frozen=True)
class FairnessEvaluationReport:
    quintile_demographic_parity_diff: float
    quintile_parity_satisfied: bool
    quintile_subgroups: List[Dict[str, Any]]
    language_parity_max_diff: float
    language_parity_satisfied: bool
    language_subgroups: List[Dict[str, Any]]
    dif_flagged_items_count: int
    dif_results: List[Dict[str, Any]]
    evidence_type: str = "synthetic_fixture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quintile_demographic_parity_diff": round(self.quintile_demographic_parity_diff, 4),
            "quintile_parity_satisfied": self.quintile_parity_satisfied,
            "quintile_subgroups": self.quintile_subgroups,
            "language_parity_max_diff": round(self.language_parity_max_diff, 4),
            "language_parity_satisfied": self.language_parity_satisfied,
            "language_subgroups": self.language_subgroups,
            "dif_flagged_items_count": self.dif_flagged_items_count,
            "dif_results": self.dif_results,
            "evidence_type": self.evidence_type,
        }


def compute_subgroup_rates(records: Sequence[Dict[str, Any]], group_key: str) -> List[SubgroupMetric]:
    """Calculate pass rate for each distinct value of group_key."""
    grouped: Dict[str, List[int]] = {}
    for r in records:
        val = str(r[group_key])
        score = int(r.get("score", 1 if r.get("first_attempt_correct") else 0))
        grouped.setdefault(val, []).append(score)

    results: List[SubgroupMetric] = []
    for g, scores in sorted(grouped.items()):
        cnt = len(scores)
        pass_cnt = sum(scores)
        rate = pass_cnt / max(1, cnt)
        results.append(
            SubgroupMetric(
                group_name=g,
                sample_size=cnt,
                pass_count=pass_cnt,
                pass_rate=round(rate, 4),
            )
        )
    return results


def compute_mantel_haenszel_dif(
    records: Sequence[Dict[str, Any]],
    focal_predicate,
    reference_predicate,
    item_id_key: str = "item_id",
    ability_key: str = "ability_group",
    score_key: str = "score",
) -> List[DIFItemResult]:
    """Compute Mantel-Haenszel Differential Item Functioning (DIF) across matched ability strata."""
    # Organize by item -> ability_stratum -> 2x2 contingency table
    items: Dict[str, Dict[str, Dict[str, int]]] = {}
    for r in records:
        item = r[item_id_key]
        stratum = str(r.get(ability_key, "all"))
        score = int(r.get(score_key, 1 if r.get("first_attempt_correct") else 0))

        is_focal = focal_predicate(r)
        is_ref = reference_predicate(r)
        if not is_focal and not is_ref:
            continue

        item_data = items.setdefault(item, {})
        cell_data = item_data.setdefault(stratum, {"A": 0, "B": 0, "C": 0, "D": 0})

        # A: focal correct, B: focal incorrect
        # C: ref correct,   D: ref incorrect
        if is_focal:
            if score == 1:
                cell_data["A"] += 1
            else:
                cell_data["B"] += 1
        elif is_ref:
            if score == 1:
                cell_data["C"] += 1
            else:
                cell_data["D"] += 1

    dif_results: List[DIFItemResult] = []
    for item, strata in items.items():
        numerator = 0.0
        denominator = 0.0
        for stratum, counts in strata.items():
            a = counts["A"]
            b = counts["B"]
            c = counts["C"]
            d = counts["D"]
            n_k = a + b + c + d
            if n_k > 0:
                numerator += (a * d) / float(n_k)
                denominator += (b * c) / float(n_k)

        if denominator <= 1e-6 or numerator <= 1e-6:
            alpha_mh = 1.0
        else:
            alpha_mh = numerator / denominator

        # ETS Delta scale: Delta_MH = -2.35 * ln(alpha_MH)
        delta_mh = -2.35 * math.log(max(1e-4, alpha_mh))
        abs_delta = abs(delta_mh)

        if abs_delta < 1.0:
            dif_class = "A"  # Negligible
        elif abs_delta < 1.5:
            dif_class = "B"  # Moderate
        else:
            dif_class = "C"  # Severe

        dif_results.append(
            DIFItemResult(
                item_id=item,
                odds_ratio=round(alpha_mh, 4),
                delta_mh=round(delta_mh, 4),
                dif_class=dif_class,
                focal_group="focal",
                reference_group="reference",
            )
        )

    return dif_results


def evaluate_educational_fairness(
    records: Sequence[Dict[str, Any]],
    quintile_tolerance: float = 0.15,
    language_tolerance: float = 0.15,
) -> FairnessEvaluationReport:
    """Evaluate fairness across SA Quintiles and Language groups, plus item-level DIF."""
    # 1. Quintiles: Group into Q1-3 (no-fee) vs Q4-5
    q13_scores: List[int] = []
    q45_scores: List[int] = []
    for r in records:
        q = int(r.get("quintile", 3))
        score = int(r.get("score", 1 if r.get("first_attempt_correct") else 0))
        if q <= 3:
            q13_scores.append(score)
        else:
            q45_scores.append(score)

    rate_q13 = (sum(q13_scores) / max(1, len(q13_scores))) if q13_scores else 0.0
    rate_q45 = (sum(q45_scores) / max(1, len(q45_scores))) if q45_scores else 0.0
    q_diff = abs(rate_q13 - rate_q45)
    q_satisfied = bool(q_diff <= quintile_tolerance)

    q_subgroups = [
        {"group_name": "Quintiles 1-3 (No-fee)", "sample_size": len(q13_scores), "pass_rate": round(rate_q13, 4)},
        {"group_name": "Quintiles 4-5", "sample_size": len(q45_scores), "pass_rate": round(rate_q45, 4)},
    ]

    # 2. Languages: English, Afrikaans, isiXhosa
    lang_metrics = compute_subgroup_rates(records, "language_group")
    lang_rates = [m.pass_rate for m in lang_metrics]
    lang_max_diff = (max(lang_rates) - min(lang_rates)) if lang_rates else 0.0
    lang_satisfied = bool(lang_max_diff <= language_tolerance)
    lang_subgroups = [asdict(m) for m in lang_metrics]

    # 3. DIF: Focal = Q1-3, Reference = Q4-5
    dif_items = compute_mantel_haenszel_dif(
        records,
        focal_predicate=lambda r: int(r.get("quintile", 3)) <= 3,
        reference_predicate=lambda r: int(r.get("quintile", 3)) >= 4,
    )
    severe_count = sum(1 for d in dif_items if d.dif_class == "C")

    return FairnessEvaluationReport(
        quintile_demographic_parity_diff=q_diff,
        quintile_parity_satisfied=q_satisfied,
        quintile_subgroups=q_subgroups,
        language_parity_max_diff=lang_max_diff,
        language_parity_satisfied=lang_satisfied,
        language_subgroups=lang_subgroups,
        dif_flagged_items_count=severe_count,
        dif_results=[asdict(d) for d in dif_items],
    )
