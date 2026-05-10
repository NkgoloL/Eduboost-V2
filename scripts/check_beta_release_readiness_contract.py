#!/usr/bin/env python3
"""Validate beta release readiness contract evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_readiness_contract.md"

REQUIRED_SNIPPETS = (
    "Beta Release Readiness Contract",
    "PR-002R backend runtime and API contract closure",
    "Phase 2 authorization closure",
    "Cluster C POPIA consent and audit closure",
    "Cluster D deployment and environment closure",
    "Cluster E data resilience closure",
    "Cluster F AI safety closure",
    "Cluster G frontend vertical journey closure",
    "OpenAPI schema drift check passes",
    "runtime entrypoint smoke checks pass",
    "authorization and consent closure checks pass",
    "database backup/restore closure checks pass",
    "AI safety fixture and prompt checks pass",
    "frontend journey closure checks pass",
    "staging release gate check passes",
    "release evidence artifact guard passes",
    "controlled validation with limited users",
    "rollback procedure",
    "privacy/POPIA sign-off",
    "make beta-release-readiness-contract-check",
)


@dataclass(frozen=True)
class BetaReleaseReadinessResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseReadinessResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaReleaseReadinessResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaReleaseReadinessResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Beta release readiness contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
