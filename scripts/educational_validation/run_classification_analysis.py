#!/usr/bin/env python3
"""Educational False-Mastery Risk Analysis CLI Runner (LEV-WS05).

Evaluates False-Mastery Rates (FMR), Wilson score 95% confidence intervals,
ROC-AUC, and asymmetric educational risk losses.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.services.educational_validation.classification import evaluate_classification_risk


def main() -> None:
    parser = argparse.ArgumentParser(description="Run educational classification and false-mastery risk analysis.")
    parser.add_argument("--data", required=True, help="Path to JSON dataset with classification_data")
    parser.add_argument("--output", help="Optional output JSON path")
    parser.add_argument("--cost-false-mastery", type=float, default=5.0)
    parser.add_argument("--cost-false-non-mastery", type=float, default=1.0)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"File not found: {data_path}", file=sys.stderr)
        sys.exit(2)

    payload = json.loads(data_path.read_text())
    cls_data = payload.get("classification_data", [])
    if not cls_data:
        print("Error: No classification_data found in input JSON.", file=sys.stderr)
        sys.exit(2)

    pred = [bool(x["predicted_mastery"]) for x in cls_data]
    true_m = [bool(x["true_mastery"]) for x in cls_data]
    scores = [float(x.get("mastery_score", 0.5)) for x in cls_data]

    metrics = evaluate_classification_risk(
        predicted_mastery=pred,
        true_mastery=true_m,
        mastery_scores=scores,
        cost_false_mastery=args.cost_false_mastery,
        cost_false_non_mastery=args.cost_false_non_mastery,
    )

    out_dict = metrics.to_dict()
    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(out_dict, indent=2) + "\n")

    print(json.dumps(out_dict, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
