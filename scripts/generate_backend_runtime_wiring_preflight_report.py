#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "release" / "backend_runtime_wiring_preflight_report.md"

COMMANDS = [
    ("runtime wiring preflight", [sys.executable, "scripts/check_backend_runtime_wiring_preflight.py"]),
    ("implementation 371-375", [sys.executable, "scripts/check_backend_implementation_371_375.py"]),
    ("implementation progress", [sys.executable, "scripts/generate_backend_consolidation_progress_report.py"]),
    ("schema drift disposable proof dry-run", [sys.executable, "scripts/run_disposable_schema_drift_proof.py", "--database-url", "postgresql+asyncpg://real_user:real_password@localhost:5432/eduboost_test", "--dry-run"]),
]


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
    rows: list[tuple[str, int, str, str]] = []
    overall = 0
    for name, command in COMMANDS:
        code, output = _run(command)
        if code != 0:
            overall = code
        rows.append((name, code, " ".join(command), output))

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Backend Runtime Wiring Preflight Report",
        "",
        f"Generated at: `{generated}`",
        "",
        "| Check | Return code | Command |",
        "|---|---:|---|",
    ]
    for name, code, command, _output in rows:
        lines.append(f"| {name} | {code} | `{command}` |")

    lines.extend(["", "## Boundary", "", "This report does not approve runtime wiring or destructive changes.", ""])
    for name, code, command, output in rows:
        lines.extend([f"## {name}", "", f"Command: `{command}`", "", f"Return code: `{code}`", "", "```text", output.rstrip(), "```", ""])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
