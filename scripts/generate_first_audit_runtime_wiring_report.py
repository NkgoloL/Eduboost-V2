#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "release" / "first_audit_runtime_wiring_report.md"

COMMANDS = [
    ("first audit runtime wiring", [sys.executable, "scripts/check_first_audit_runtime_wiring.py"]),
    ("destructive-action guard", [sys.executable, "scripts/check_first_audit_runtime_wiring_no_destructive_actions.py"]),
    ("runtime enablement guard", [sys.executable, "scripts/check_backend_runtime_enablement_guard.py"]),
    ("first wiring candidates", [sys.executable, "scripts/check_backend_first_wiring_candidates.py"]),
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
        "# First Audit Runtime Wiring Report",
        "",
        f"Generated at: `{generated}`",
        "",
        "| Check | Return code | Command |",
        "|---|---:|---|",
    ]
    for name, code, command, _output in rows:
        lines.append(f"| {name} | {code} | `{command}` |")

    lines.extend(["", "## Boundary", "", "This report covers one non-destructive audit runtime wiring candidate only.", ""])
    for name, code, command, output in rows:
        lines.extend([f"## {name}", "", f"Command: `{command}`", "", f"Return code: `{code}`", "", "```text", output.rstrip(), "```", ""])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
