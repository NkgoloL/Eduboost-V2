#!/usr/bin/env python3
"""Educational Model Calibration Analysis CLI Runner (LEV-WS04).

Evaluates Expected Calibration Error (ECE), Brier score, and bin reliability.
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run educational model calibration analysis.")
    parser.add_argument("--data", required=True, help="Path to JSON dataset containing calibration_data")
    parser.add_argument("--output", help="Optional output JSON path")
    parser.add_argument("--ece-tolerance", type=float, default=0.15)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"File not found: {data_path}", file=sys.stderr)
        sys.exit(2)

    payload = json.loads(data_path.read_text())
    cal_data = payload.get("calibration_data", [])
    if not cal_data:
        print("Error: No calibration_data found in input JSON.", file=sys.stderr)
        sys.exit(2)

    probs = [x["predicted_prob"] for x in cal_data]
    outs = [x["outcome"] for x in cal_data]

    metrics = evaluate_model_calibration(
        probabilities=probs,
        outcomes=outs,
        ece_tolerance=args.ece_tolerance,
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
