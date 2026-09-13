"""Verify PRD-11.3R documentation-defined coverage contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from scripts.coverage_suites.coverage_contract import (
    ROOT,
    evaluate_coverage_contract,
    evaluate_empirical_coverage,
    evaluate_threshold_alignment,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--threshold-only", action="store_true")
    parser.add_argument("--check-empirical", action="store_true", help="Verify empirical coverage XML meets 90% floor")
    parser.add_argument("--coverage-xml", type=str, default=None, help="Path to coverage.xml")
    parser.add_argument("--skip-freshness", action="store_true")
    args = parser.parse_args()
    if args.check_empirical:
        coverage_path = Path(args.coverage_xml) if args.coverage_xml else None
        result = evaluate_empirical_coverage(ROOT, coverage_xml_path=coverage_path)
    elif args.threshold_only:
        result = evaluate_threshold_alignment(ROOT)
    else:
        result = evaluate_coverage_contract(ROOT, require_freshness=not args.skip_freshness)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())

