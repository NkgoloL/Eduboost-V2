#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.services.audit_canonicalization_registry import ready_candidates, unsafe_candidates


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures: list[str] = []
    print("Audit canonicalization migration registry check")

    ready = ready_candidates()
    unsafe = unsafe_candidates()

    if ready:
        print(f"- PASS ready non-destructive candidates: {len(ready)}")
        for candidate in ready:
            print(f"  - {candidate.name}: {candidate.status.value}")
    else:
        print("- FAIL no ready non-destructive candidates")
        failures.append("no ready candidates")

    if not unsafe:
        print("- PASS no destructive candidates are marked ready")
    else:
        print("- FAIL destructive candidates present")
        failures.extend(candidate.name for candidate in unsafe)

    doc = REPO_ROOT / "docs/release/audit_canonicalization_migration_registry.md"
    if doc.exists() and "Legacy deletion remains blocked" in doc.read_text(encoding="utf-8"):
        print("- PASS audit migration registry doc present")
    else:
        print("- FAIL audit migration registry doc missing/incomplete")
        failures.append("registry doc missing")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
