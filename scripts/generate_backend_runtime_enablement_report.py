#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs/release/backend_runtime_enablement_report.md"
CHECKSUM_OUTPUT = REPO_ROOT / "docs/release/backend_runtime_enablement_checksum_manifest.md"

COMMANDS = [
    ("runtime enablement guard", [sys.executable, "scripts/check_backend_runtime_enablement_guard.py"]),
    ("destructive action blocklist", [sys.executable, "scripts/check_backend_destructive_action_blocklist.py"]),
    ("first wiring candidates", [sys.executable, "scripts/check_backend_first_wiring_candidates.py"]),
    ("runtime wiring cases", [sys.executable, "scripts/check_backend_runtime_wiring_cases.py"]),
]

ARTIFACTS = [
    "docs/release/backend_runtime_enablement_packet.md",
    "docs/release/audit_candidate_execution_ledger.md",
    "docs/release/consent_candidate_execution_ledger.md",
    "docs/release/deep_readiness_implementation_blueprint.md",
    "docs/release/schema_drift_real_db_execution_packet.md",
    "docs/release/runtime_wiring_approval_checklist.md",
    "docs/release/backend_data_retention_approval_update.md",
    "docs/pr/backend_runtime_wiring_pr_template.md",
    "docs/release/backend_implementation_manifest_401_420.md",
    "docs/release/release_owner_runtime_wiring_signoff_template.md",
    "docs/release/backend_runtime_enablement_closure_packet.md",
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _write_checksum_manifest() -> None:
    lines = ["# Backend Runtime Enablement Checksum Manifest", "", "| Path | SHA-256 |", "|---|---|"]
    for relative in ARTIFACTS:
        path = REPO_ROOT / relative
        if path.exists():
            lines.append(f"| `{relative}` | `{_sha256(path)}` |")
        else:
            lines.append(f"| `{relative}` | `MISSING` |")
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
        "# Backend Runtime Enablement Report",
        "",
        f"Generated at: `{generated}`",
        "",
        "| Check | Return code | Command |",
        "|---|---:|---|",
    ]
    for name, code, command, _output in rows:
        lines.append(f"| {name} | {code} | `{command}` |")

    lines.extend(["", "## Boundary", "", "This report enables a scoped runtime PR only. It does not approve destructive consolidation.", ""])
    for name, code, command, output in rows:
        lines.extend([f"## {name}", "", f"Command: `{command}`", "", f"Return code: `{code}`", "", "```text", output.rstrip(), "```", ""])

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {CHECKSUM_OUTPUT}")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
