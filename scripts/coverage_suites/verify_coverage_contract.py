"""Verify PRD-11.3R documentation-defined coverage contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from scripts.coverage_suites.coverage_contract import (
    ROOT,
    evaluate_coverage_contract,
    evaluate_measured_coverage,
    evaluate_threshold_alignment,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--threshold-only", action="store_true")
    parser.add_argument("--require-report", action="store_true")
    parser.add_argument("--report-path", type=Path, default=None)
    parser.add_argument("--min-percent", type=float, default=90.0)
    parser.add_argument("--skip-freshness", action="store_true")
    args = parser.parse_args()
    if args.threshold_only:
        result = evaluate_threshold_alignment(ROOT)
    elif args.require_report:
        result = evaluate_measured_coverage(ROOT, report_path=args.report_path, min_percent=args.min_percent)
    else:
        result = evaluate_coverage_contract(ROOT, require_freshness=not args.skip_freshness)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())

