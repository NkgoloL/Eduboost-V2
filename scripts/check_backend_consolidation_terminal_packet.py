#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    Path(".github/workflows/backend-consolidation.yml"),
    Path("docs/release/backend_consolidation_terminal_packet.md"),
    Path("docs/release/backend_consolidation_evidence_manifest.md"),
    Path("scripts/generate_backend_consolidation_evidence_manifest.py"),
    Path("scripts/generate_backend_consolidation_terminal_report.py"),
]

COMMANDS = [
    [sys.executable, "scripts/check_backend_consolidation_execution_packet.py"],
    [sys.executable, "scripts/check_backend_consolidation_noop_guard.py"],
    [sys.executable, "scripts/check_backend_consolidation_release_guard.py"],
    [sys.executable, "scripts/check_backend_runtime_compatibility.py"],
    [sys.executable, "scripts/check_backend_runtime_probe_fixtures.py"],
]


def main() -> int:
    failures: list[str] = []
    print("Backend consolidation terminal packet check")

    for relative in REQUIRED_FILES:
        path = REPO_ROOT / relative
        if path.exists():
            print(f"- PASS [file] {relative}: present")
        else:
            print(f"- FAIL [file] {relative}: missing")
            failures.append(f"missing {relative}")

    packet = REPO_ROOT / "docs/release/backend_consolidation_terminal_packet.md"
    if packet.exists():
        text = packet.read_text(encoding="utf-8")
        for needle in ["does not authorize implementation or deletion", "full test suite green", "migration evidence"]:
            if needle in text:
                print(f"- PASS [packet] contains {needle!r}")
            else:
                print(f"- FAIL [packet] missing {needle!r}")
                failures.append(f"packet missing {needle!r}")

    for command in COMMANDS:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("command failed: " + " ".join(command))

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend consolidation terminal packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
