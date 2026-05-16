#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "release" / "backend_consolidation_readiness_report.md"
COMMANDS = [
    ("backend consolidation report", [sys.executable, "scripts/generate_backend_consolidation_report.py"]),
    ("runtime compatibility report", [sys.executable, "scripts/generate_backend_runtime_compatibility_report.py"]),
    ("deletion candidate inventory", [sys.executable, "scripts/generate_backend_deletion_candidate_inventory.py", "--fail-empty"]),
    ("no-op guard", [sys.executable, "scripts/check_backend_consolidation_noop_guard.py"]),
]

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode, result.stdout

def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, int, str, str]] = []
    overall = 0
    for name, command in COMMANDS:
        code, output = _run(command)
        if code != 0:
            overall = code
        rows.append((name, code, " ".join(command), output))
    lines = [
        "# Backend Consolidation Readiness Report",
        "",
        f"Generated at: `{_utc_now()}`",
        "",
        "| Check | Return code | Command |",
        "|---|---:|---|",
    ]
    for name, code, command, _output in rows:
        lines.append(f"| {name} | {code} | `{command}` |")
    lines.extend(["", "## Boundary", "", "This report does not approve deletion, table merging, Alembic stamping, or runtime rewiring.", ""])
    for name, code, command, output in rows:
        lines.extend([f"## {name}", "", f"Command: `{command}`", "", f"Return code: `{code}`", "", "```text", output.rstrip(), "```", ""])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return overall

if __name__ == "__main__":
    raise SystemExit(main())
