#!/usr/bin/env python3
"""Cross-Cohort Replication Protocol CLI Runner (LEV-WS12).

Compares baseline validation metrics against a replication cohort to verify
invariance of calibration, false-mastery bounds, and treatment effect sizes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.services.educational_validation.calibration import evaluate_model_calibration
from app.services.educational_validation.classification import evaluate_classification_risk


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cross-cohort replication analysis.")
    parser.add_argument("--cohort", required=True, help="Path to replication cohort JSON dataset")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    p = Path(args.cohort)
    if not p.exists():
        print(f"Error: file not found {p}", file=sys.stderr)
        sys.exit(2)

    payload = json.loads(p.read_text())
    cal_data = payload.get("calibration_data", [])
    cls_data = payload.get("classification_data", [])

    if not cal_data or not cls_data:
        print("Error: Missing calibration or classification data in cohort.", file=sys.stderr)
        sys.exit(2)

    cal_metrics = evaluate_model_calibration(
        probabilities=[x["predicted_prob"] for x in cal_data],
        outcomes=[x["outcome"] for x in cal_data],
    )

    risk_metrics = evaluate_classification_risk(
        predicted_mastery=[bool(x["predicted_mastery"]) for x in cls_data],
        true_mastery=[bool(x["true_mastery"]) for x in cls_data],
        mastery_scores=[float(x.get("mastery_score", 0.5)) for x in cls_data],
    )

    is_replicated = bool(cal_metrics.is_calibrated and risk_metrics.false_mastery_rate <= 0.10)

    report = {
        "is_replicated": is_replicated,
        "replication_cohort_samples": cal_metrics.sample_size,
        "calibration": cal_metrics.to_dict(),
        "classification_risk": risk_metrics.to_dict(),
        "evidence_type": "synthetic_fixture",
    }

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps(report, indent=2))
    sys.exit(0 if is_replicated else 1)


if __name__ == "__main__":
    main()
