#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    Path("docs/adr/ADR-021-backend-consolidation-evidence-first.md"),
    Path("docs/release/backend_consolidation_dragons.md"),
    Path("docs/release/backend_consolidation_decision_record.md"),
    Path("docs/release/audit_repository_compatibility_contract.md"),
    Path("docs/release/consent_service_compatibility_contract.md"),
    Path("docs/release/health_readiness_diagnostic_contract.md"),
    Path("docs/release/schema_drift_evidence_contract.md"),
    Path("app/repositories/audit_compat.py"),
    Path("app/services/consent_compat.py"),
    Path("scripts/generate_backend_consolidation_report.py"),
]

FORBIDDEN_APPROVAL_PHRASES = [
    "deletion approved",
    "fresh start acceptable",
    "discard historical audit",
    "stamp head as repair",
]


def main() -> int:
    failures: list[str] = []
    print("Backend consolidation release guard")

    for relative in REQUIRED_FILES:
        path = REPO_ROOT / relative
        if path.exists():
            print(f"- PASS [file] {relative}: present")
        else:
            print(f"- FAIL [file] {relative}: missing")
            failures.append(f"missing {relative}")

    decision = REPO_ROOT / "docs/release/backend_consolidation_decision_record.md"
    if decision.exists():
        text = decision.read_text(encoding="utf-8").lower()
        if "status:** pending implementation decisions" in text or "status: pending implementation decisions" in text:
            print("- PASS [decision] consolidation decisions remain pending")
        else:
            print("- FAIL [decision] decision record status marker missing")
            failures.append("decision record status marker missing")

        for phrase in FORBIDDEN_APPROVAL_PHRASES:
            if phrase in text:
                print(f"- FAIL [decision] forbidden premature approval phrase: {phrase!r}")
                failures.append(f"forbidden phrase {phrase!r}")
            else:
                print(f"- PASS [decision] no premature approval phrase: {phrase!r}")

    report = REPO_ROOT / "docs/release/backend_consolidation_diagnostic_report.md"
    if report.exists():
        print("- PASS [report] diagnostic report present")
    else:
        print("- WARN [report] diagnostic report not generated yet; run make backend-consolidation-report")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend consolidation release guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
