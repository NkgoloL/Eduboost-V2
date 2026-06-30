#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "release" / "backend_first_wiring_candidates_report.md"

COMMANDS = [
    ("first wiring candidates", [sys.executable, "scripts/check_backend_first_wiring_candidates.py"]),
    ("runtime wiring cases", [sys.executable, "scripts/check_backend_runtime_wiring_cases.py"]),
    ("runtime wiring preflight", [sys.executable, "scripts/check_backend_runtime_wiring_preflight.py"]),
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
        "# Backend First Wiring Candidates Report",
        "",
        f"Generated at: `{generated}`",
        "",
        "| Check | Return code | Command |",
        "|---|---:|---|",
    ]
    for name, code, command, _output in rows:
        lines.append(f"| {name} | {code} | `{command}` |")

    lines.extend(["", "## Boundary", "", "This report proves first wiring candidates only; it does not approve route rewiring or destructive changes.", ""])
    for name, code, command, output in rows:
        lines.extend([f"## {name}", "", f"Command: `{command}`", "", f"Return code: `{code}`", "", "```text", output.rstrip(), "```", ""])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
