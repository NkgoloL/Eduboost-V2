"""Verify PRD-11.0R Execution-6 product critical-flow green contract."""
from __future__ import annotations

import argparse
import json

from scripts.test_suites.product_critical_flow_green import ROOT, evaluate_product_critical_flow_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate_product_critical_flow_contract(ROOT, require_green=args.require_green)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
