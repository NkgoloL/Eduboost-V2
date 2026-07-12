"""Verify the Execution-7 coverage baseline stabilisation contract."""
from __future__ import annotations

import argparse
import json

from scripts.coverage_suites.coverage_baseline_stabilisation import (
    ROOT,
    evaluate_coverage_baseline_stabilisation_contract,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate_coverage_baseline_stabilisation_contract(
        ROOT,
        require_green=args.require_green,
    )
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
