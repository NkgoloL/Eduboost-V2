#!/usr/bin/env python3
"""Validate audit evidence for denied consent-protected learner-data access."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIREMENTS = {
    "app/modules/consent/service.py": (
        "require_active_consent",
        "consent.access_rejected",
        "ConsentExpiredError",
        "ConsentRequiredError",
        "_append_audit",
    ),
    "app/core/audit.py": (
        "access_rejected",
        "constitutional_outcome=\"REJECTED\"",
    ),
    "docs/security/audit_event_contracts.md": (
        "consent access-rejected audit event",
    ),
}


@dataclass(frozen=True)
class AuditResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[AuditResult]:
    results: list[AuditResult] = []
    for rel_path, snippets in REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                AuditResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )
    return results


def main() -> int:
    results = run_checks()
    print("Consent rejection audit check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
