#!/usr/bin/env python3
"""Educational Model Drift Check CLI (LEV-WS13).

Runs Population Stability Index (PSI), Kolmogorov-Smirnov (KS) tests,
and Wasserstein distance checks on educational model mastery score distributions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.services.educational_validation.drift import evaluate_model_drift


def main() -> None:
    parser = argparse.ArgumentParser(description="Check educational model drift between baseline and target distributions.")
    parser.add_argument("--data", help="Path to JSON dataset containing drift_data or events")
    parser.add_argument("--baseline-file", help="Path to JSON array of baseline float scores")
    parser.add_argument("--current-file", help="Path to JSON array of current float scores")
    parser.add_argument("--output", help="Optional output JSON path")
    parser.add_argument("--psi-warning", type=float, default=0.10)
    parser.add_argument("--psi-critical", type=float, default=0.20)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    baseline_scores = None
    current_scores = None

    if args.data:
        data_path = Path(args.data)
        if not data_path.exists():
            print(f"Data file not found: {data_path}", file=sys.stderr)
            sys.exit(2)
        payload = json.loads(data_path.read_text())
        if "drift_data" in payload:
            baseline_scores = payload["drift_data"].get("baseline_scores", [])
            current_scores = payload["drift_data"].get("target_scores", [])
        elif "baseline_scores" in payload and "target_scores" in payload:
            baseline_scores = payload["baseline_scores"]
            current_scores = payload["target_scores"]
        elif "classification_data" in payload:
            # Fallback: extract mastery scores
            scores = [x["mastery_score"] for x in payload["classification_data"] if "mastery_score" in x]
            half = len(scores) // 2
            baseline_scores = scores[:half]
            current_scores = scores[half:]

    if args.baseline_file and args.current_file:
        baseline_scores = json.loads(Path(args.baseline_file).read_text())
        current_scores = json.loads(Path(args.current_file).read_text())

    if not baseline_scores or not current_scores:
        print("Error: Could not extract baseline and current scores from input.", file=sys.stderr)
        sys.exit(2)

    result = evaluate_model_drift(
        baseline=baseline_scores,
        current=current_scores,
        psi_warning=args.psi_warning,
        psi_critical=args.psi_critical,
    )

    out_dict = result.to_dict()
    out_dict["evidence_type"] = "synthetic_fixture"

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(out_dict, indent=2) + "\n")

    print(json.dumps(out_dict, indent=2))
    # Return exit code 0 if stable/warning, 1 if critical
    if result.alert_required:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
