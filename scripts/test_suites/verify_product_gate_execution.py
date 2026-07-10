"""Verify PRD-11.0R RESTORE-4 product gate execution contract."""
from __future__ import annotations

import argparse
import json

from scripts.test_suites.product_gate_execution import ROOT, evaluate_product_gate_execution_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate_product_gate_execution_contract(ROOT)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
