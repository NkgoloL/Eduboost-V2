#!/usr/bin/env python3
"""Validate post-deploy staging smoke checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "post_deploy_staging_smoke_checklist.md"

REQUIRED_SNIPPETS = (
    "Post-Deploy Staging Smoke Checklist",
    "Backend Smoke Checks",
    "canonical `app.api_v2:app` import remains valid",
    "OpenAPI schema matches committed contract",
    "global error envelope remains canonical",
    "Security and Compliance Smoke Checks",
    "authorization denial returns safe response",
    "consent-required denial returns safe response",
    "POPIA audit event path remains available",
    "Data Resilience Smoke Checks",
    "backup manifest exists",
    "restore evidence exists",
    "production restore approval remains enforced",
    "AI Safety Smoke Checks",
    "AI fixture validation passes",
    "prompt secret leakage guard passes",
    "Frontend Smoke Checks",
    "learner journey entrypoint loads",
    "parent journey entrypoint loads",
    "accessibility static check passes",
    "auth/consent denial UX contract passes",
    "make post-deploy-staging-smoke-checklist-check",
)


@dataclass(frozen=True)
class PostDeploySmokeChecklistResult:
    ok: bool
    detail: str


def run_checks() -> list[PostDeploySmokeChecklistResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        PostDeploySmokeChecklistResult(DOC.exists(), "checklist present" if DOC.exists() else "checklist missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PostDeploySmokeChecklistResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Post-deploy staging smoke checklist check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
