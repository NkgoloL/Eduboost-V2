"""List or execute generated-contract and frontend-quality gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.advisory_suites.generated_frontend_quality_gate import ROOT, execute_gate_plan, gate_command_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--gate", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.execute:
        payload = execute_gate_plan(ROOT, gates=args.gate)
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
        return 0 if payload.get("all_green") else 1
    payload = {"executed": False, "commands": gate_command_plan(ROOT)}
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
