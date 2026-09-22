#!/usr/bin/env python3
"""Educational Fairness & Differential Item Functioning CLI Runner (LEV-WS09).

Evaluates parity bands across South African Quintiles and official Languages,
along with Mantel-Haenszel DIF item analysis.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.services.educational_validation.fairness import evaluate_educational_fairness


def main() -> None:
    parser = argparse.ArgumentParser(description="Run educational fairness and DIF analysis.")
    parser.add_argument("--data", required=True, help="Path to JSON dataset with fairness_data or events")
    parser.add_argument("--output", help="Optional output JSON path")
    parser.add_argument("--quintile-tolerance", type=float, default=0.15)
    parser.add_argument("--language-tolerance", type=float, default=0.15)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"File not found: {data_path}", file=sys.stderr)
        sys.exit(2)

    payload = json.loads(data_path.read_text())
    fair_data = payload.get("fairness_data", [])
    if not fair_data and "events" in payload:
        fair_data = payload["events"]

    if not fair_data:
        print("Error: No fairness data or events found in input JSON.", file=sys.stderr)
        sys.exit(2)

    report = evaluate_educational_fairness(
        records=fair_data,
        quintile_tolerance=args.quintile_tolerance,
        language_tolerance=args.language_tolerance,
    )

    out_dict = report.to_dict()
    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(out_dict, indent=2) + "\n")

    print(json.dumps(out_dict, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
