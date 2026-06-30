#!/usr/bin/env python3
"""Validate frontend authorization/consent denial UX evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_auth_consent_denial_contract.md"

REQUIRED_SNIPPETS = (
    "Frontend Auth Consent Denial Contract",
    "unauthenticated session",
    "unauthorized learner access",
    "unauthorized parent access",
    "inactive or expired consent",
    "revoked consent",
    "missing learner link",
    "denial states must not expose another learner's data",
    "denial states must show safe next action",
    "authorization denial must not offer bypass instructions",
    "learner-facing copy must remain age-appropriate",
    "route or component handling 401/403",
    "API client branch for error envelope parsing",
    "make frontend-auth-consent-denial-check",
)


@dataclass(frozen=True)
class FrontendDenialResult:
    ok: bool
    detail: str


def run_checks() -> list[FrontendDenialResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        FrontendDenialResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FrontendDenialResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend auth/consent denial contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
