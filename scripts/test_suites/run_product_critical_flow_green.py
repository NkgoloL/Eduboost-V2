"""Run PRD-11.0R Execution-6 product critical-flow green commands."""
from __future__ import annotations

import argparse
import json

from scripts.test_suites.product_critical_flow_green import run_product_flow_green


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = run_product_flow_green(execute=args.execute)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    if args.require_green and payload.get("all_green") is not True:
        return 1
    return 0 if payload.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
