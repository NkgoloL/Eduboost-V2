"""List or execute the PRD-11.0R.EXECUTION-3 generated/frontend green run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.advisory_suites.generated_contract_frontend_green_run import ROOT, execute_green_run, green_run_command_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--gate", action="append", default=[])
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.execute:
        payload = execute_green_run(
            ROOT,
            gates=args.gate,
            output_dir=args.output_dir,
            continue_on_failure=not args.fail_fast,
        )
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
        return 0 if payload.get("all_green") else 1
    payload = {"executed": False, "commands": green_run_command_plan(ROOT)}
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
