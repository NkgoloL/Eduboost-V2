#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "release" / "backend_consolidation_diagnostic_report.md"

COMMANDS = [
    ("backend dragons", [sys.executable, "scripts/check_backend_consolidation_dragons.py"]),
    ("audit inventory", [sys.executable, "scripts/generate_audit_callsite_inventory.py", "--fail-empty"]),
    ("consent inventory", [sys.executable, "scripts/generate_consent_callsite_inventory.py", "--fail-empty"]),
    ("health readiness contract", [sys.executable, "scripts/check_health_readiness_contract.py"]),
    ("schema drift contract", [sys.executable, "scripts/check_schema_drift_contract.py"]),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_command(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode, result.stdout


def generate() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, int, str, str]] = []
    overall = 0
    for name, command in COMMANDS:
        code, output = run_command(command)
        if code != 0:
            overall = code
        rows.append((name, code, " ".join(command), output))

    lines = [
        "# Backend Consolidation Diagnostic Report",
        "",
        f"Generated at: `{_utc_now()}`",
        "",
        "| Check | Return code | Command |",
        "|---|---:|---|",
    ]

    for name, code, command, _output in rows:
        lines.append(f"| {name} | {code} | `{command}` |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This report is diagnostic evidence only.",
            "- It does not approve deletion of audit or consent code.",
            "- It does not approve consent table consolidation.",
            "- It does not approve Alembic stamping/baselining.",
            "",
        ]
    )

    for name, code, command, output in rows:
        lines.extend(
            [
                f"## {name}",
                "",
                f"Command: `{command}`",
                "",
                f"Return code: `{code}`",
                "",
                "```text",
                output.rstrip(),
                "```",
                "",
            ]
        )

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return overall


def main() -> int:
    return generate()


if __name__ == "__main__":
    raise SystemExit(main())
