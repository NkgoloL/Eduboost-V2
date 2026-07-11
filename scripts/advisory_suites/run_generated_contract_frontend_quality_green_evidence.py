"""List or execute PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4 green-evidence gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.advisory_suites.generated_contract_frontend_quality_green_evidence import (
    ROOT,
    execute_green_evidence,
    green_evidence_command_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--gate", action="append", default=[])
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.execute:
        payload = execute_green_evidence(
            ROOT,
            gates=args.gate,
            output_dir=args.output_dir,
            continue_on_failure=not args.fail_fast,
        )
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
        return 0 if payload.get("all_green") else 1
    payload = {"executed": False, "commands": green_evidence_command_plan(ROOT)}
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
