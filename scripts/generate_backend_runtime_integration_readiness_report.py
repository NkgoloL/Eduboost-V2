#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "release" / "backend_runtime_integration_readiness_report.md"
CHECKSUM_OUTPUT = REPO_ROOT / "docs" / "release" / "backend_runtime_integration_checksum_manifest.md"

COMMANDS = [
    ("runtime integration readiness", [sys.executable, "scripts/check_backend_runtime_integration_readiness.py"]),
    ("runtime integration blocklists", [sys.executable, "scripts/check_backend_runtime_integration_blocklists.py"]),
    ("431-450 wiring", [sys.executable, "scripts/check_first_consent_and_deep_readiness_runtime_wiring.py"]),
    ("421-430 wiring", [sys.executable, "scripts/check_first_audit_runtime_wiring.py"]),
]

ARTIFACTS = [
    "docs/release/backend_runtime_integration_readiness.md",
    "docs/release/audit_runtime_integration_target_map.md",
    "docs/release/consent_runtime_integration_target_map.md",
    "docs/release/deep_readiness_runtime_integration_target_map.md",
    "docs/release/runtime_integration_boundary_policy.md",
    "docs/pr/runtime_integration_pr_template.md",
    "docs/release/runtime_integration_rollback_checklist.md",
    "docs/release/backend_runtime_integration_next_pr_queue.md",
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


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_checksum_manifest() -> None:
    lines = ["# Backend Runtime Integration Checksum Manifest", "", "| Path | SHA-256 |", "|---|---|"]
    for relative in ARTIFACTS:
        path = REPO_ROOT / relative
        lines.append(f"| `{relative}` | `{_sha(path) if path.exists() else 'MISSING'}` |")
    CHECKSUM_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows: list[tuple[str, int, str, str]] = []
    overall = 0
    for name, command in COMMANDS:
        code, output = _run(command)
        if code != 0:
            overall = code
        rows.append((name, code, " ".join(command), output))

    _write_checksum_manifest()

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Backend Runtime Integration Readiness Report",
        "",
        f"Generated at: `{generated}`",
        "",
        "| Check | Return code | Command |",
        "|---|---:|---|",
    ]
    for name, code, command, _output in rows:
        lines.append(f"| {name} | {code} | `{command}` |")

    lines.extend(["", "## Boundary", "", "This report authorizes PR planning only, not runtime route registration or destructive changes.", ""])
    for name, code, command, output in rows:
        lines.extend([f"## {name}", "", f"Command: `{command}`", "", f"Return code: `{code}`", "", "```text", output.rstrip(), "```", ""])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {CHECKSUM_OUTPUT}")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
