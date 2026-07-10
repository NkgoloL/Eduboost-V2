"""List or execute PRD-11.0R RESTORE-4 product critical-flow commands."""
from __future__ import annotations

import argparse
import json
import subprocess
from typing import Any

from scripts.test_suites.product_gate_execution import flow_command_plan


def _select(commands: list[dict[str, Any]], flow: str | None) -> list[dict[str, Any]]:
    if not flow:
        return commands
    return [item for item in commands if item.get("flow_id") == flow]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    commands = _select(flow_command_plan(), args.flow)
    if args.flow and not commands:
        raise SystemExit(f"unknown flow: {args.flow}")
    if not args.execute:
        payload = {"valid": True, "executed": False, "commands": commands}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
        return 0
    results = []
    exit_code = 0
    for item in commands:
        for kind in ("positive", "negative"):
            command = item[f"{kind}_command"]
            completed = subprocess.run(command, shell=True, text=True, capture_output=True)
            results.append({
                "flow_id": item["flow_id"],
                "kind": kind,
                "command": command,
                "exit_code": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
            })
            if completed.returncode != 0:
                exit_code = completed.returncode
    payload = {"valid": exit_code == 0, "executed": True, "results": results}
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
