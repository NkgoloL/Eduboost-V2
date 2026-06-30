#!/usr/bin/env python3
"""Run the backend fast gate and write reproducible raw evidence."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def run_backend_fast(command: str, output_dir: Path, root: Path = ROOT) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "backend_fast_gate.txt"
    result_path = output_dir / "backend_fast_gate_result.json"

    env = os.environ.copy()
    env.setdefault("PYTHONPATH", ".")
    started = time.time()
    completed = subprocess.run(
        command,
        cwd=root,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        timeout=int(env.get("BACKEND_FAST_TIMEOUT_SECONDS", "1800")),
    )
    elapsed = time.time() - started
    output_path.write_text(completed.stdout, encoding="utf-8", errors="replace")
    payload: dict[str, Any] = {
        "valid": completed.returncode == 0,
        "command": command,
        "command_tokens": shlex.split(command),
        "returncode": completed.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "output_path": str(output_path),
    }
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", default=os.environ.get("BACKEND_FAST_COMMAND", "make test-fast"))
    parser.add_argument("--output-dir", type=Path, default=Path("var/audit-remediation/backend-fast"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_backend_fast(args.command, args.output_dir.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST GATE PASSED" if result["valid"] else "BACKEND FAST GATE FAILED")
        print(f"command: {result['command']}")
        print(f"returncode: {result['returncode']}")
        print(f"output: {result['output_path']}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
