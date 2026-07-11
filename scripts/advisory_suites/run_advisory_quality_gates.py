"""List or execute PRD-11.0R.RUNTIME-RESTORE-5 advisory quality gate commands."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from typing import Any

from scripts.advisory_suites.advisory_gate import gate_command_plan


def _run(command: str) -> dict[str, Any]:
    completed = subprocess.run(command, shell=True, text=True, capture_output=True)
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Run commands instead of listing them.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    plan = gate_command_plan()
    if not args.execute:
        payload = {"executed": False, "commands": plan}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
        return 0
    results = []
    for item in plan:
        results.append({**item, "result": _run(item["command"])})
    payload = {"executed": True, "results": results, "all_green": all(item["result"]["exit_code"] == 0 for item in results)}
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return 0 if payload["all_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
