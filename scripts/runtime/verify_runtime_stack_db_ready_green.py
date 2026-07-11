"""Verify PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5 runtime green evidence contract."""
from __future__ import annotations

import argparse
import json

from scripts.runtime.runtime_stack_db_ready_green import ROOT, evaluate_runtime_green_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-green", action="store_true")
    args = parser.parse_args()
    result = evaluate_runtime_green_contract(ROOT, require_green=args.require_green)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
