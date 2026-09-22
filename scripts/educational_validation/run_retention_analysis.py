#!/usr/bin/env python3
"""Educational Spaced Retention Multi-Model Decay CLI Runner (LEV-WS06).

Fits Exponential, Power-Law, and Two-Component memory decay functions
and selects the best fitting model by AIC/BIC/RMSE.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.services.educational_validation.retention import fit_multi_model_retention


def main() -> None:
    parser = argparse.ArgumentParser(description="Run educational spaced retention multi-model decay analysis.")
    parser.add_argument("--data", required=True, help="Path to JSON dataset containing retention_records")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"File not found: {data_path}", file=sys.stderr)
        sys.exit(2)

    payload = json.loads(data_path.read_text())
    recs = payload.get("retention_records", [])
    if not recs:
        print("Error: No retention_records found in data file.", file=sys.stderr)
        sys.exit(2)

    days = [int(r["days_elapsed"]) for r in recs]
    scores = [float(r["retention_score"]) for r in recs]

    report = fit_multi_model_retention(days, scores)

    out_dict = report.to_dict()
    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(out_dict, indent=2) + "\n")

    print(json.dumps(out_dict, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
