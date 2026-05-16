#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    Path("app/services/backend_consolidation_runtime.py"): [
        "record_canonical_audit_event",
        "record_consent_audit_event",
        "probe_constructor",
    ],
    Path("docs/adr/ADR-022-audit-consent-table-ownership-options.md"): [
        "Option A",
        "Option B",
        "Option C",
        "Option D",
        "Not approved",
    ],
    Path("docs/release/backend_consolidation_implementation_foundation.md"): [
        "non-destructive implementation foundation",
        "Explicitly excluded",
    ],
}

FORBIDDEN = [
    "deletion approved",
    "fresh start approved",
    "discard audit history",
    "drop consent history",
    "stamp head as repair approved",
]


def main() -> int:
    failures: list[str] = []
    print("Backend consolidation implementation foundation check")

    for relative, needles in REQUIRED_FILES.items():
        path = REPO_ROOT / relative
        if path.exists():
            print(f"- PASS [file] {relative}: present")
        else:
            print(f"- FAIL [file] {relative}: missing")
            failures.append(f"missing {relative}")
            continue

        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        for needle in needles:
            if needle in text:
                print(f"- PASS [content] {relative}: contains {needle!r}")
            else:
                print(f"- FAIL [content] {relative}: missing {needle!r}")
                failures.append(f"{relative} missing {needle!r}")
        for phrase in FORBIDDEN:
            if phrase in lower:
                print(f"- FAIL [guard] {relative}: forbidden phrase {phrase!r}")
                failures.append(f"forbidden phrase {phrase!r}")

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "app/services/backend_consolidation_runtime.py"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode == 0:
        print("- PASS [compile] backend_consolidation_runtime.py")
    else:
        print(result.stdout)
        failures.append("backend_consolidation_runtime.py compile failed")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend consolidation implementation foundation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
