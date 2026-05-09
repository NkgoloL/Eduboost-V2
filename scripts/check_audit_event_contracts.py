#!/usr/bin/env python3
"""Check baseline POPIA/security audit-event contract markers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


REQUIREMENTS = {
    "app/core/audit.py": (
        "class FourthEstateService",
        "async def record",
        "async def consent_granted",
        "async def consent_revoked",
        "async def erasure_requested",
        "async def erasure_executed",
        "async def access_rejected",
    ),
    "app/modules/consent/service.py": (
        "require_active_consent",
        "consent.access_rejected",
        "consent.granted",
        "consent.revoked",
        "consent.renewed",
        "consent.erasure_requested",
        "FourthEstateService",
    ),
    "app/api_v2_routers/consent.py": (
        "ConsentService(db).grant",
        "ConsentService(db).revoke",
        "AuditLog emission is handled inside ConsentService",
    ),
}


@dataclass(frozen=True)
class CheckResult:
    path: str
    marker: str
    ok: bool


def run_checks() -> list[CheckResult]:
    results: list[CheckResult] = []
    for rel_path, markers in REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for marker in markers:
            results.append(CheckResult(rel_path, marker, marker in text))
    return results


def main() -> int:
    results = run_checks()
    print("Audit event contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.path}: contains {result.marker!r}")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
