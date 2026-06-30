#!/usr/bin/env python3
"""Validate release owner accountability matrix."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_owner_accountability_matrix.md"

REQUIRED_SNIPPETS = (
    "Release Owner Accountability Matrix",
    "Release operation",
    "release operator",
    "Technical approval",
    "technical approver",
    "Privacy/POPIA approval",
    "privacy/POPIA approver",
    "Rollback readiness",
    "rollback owner",
    "Post-deploy verification",
    "post-deploy verification owner",
    "Incident response",
    "incident contact",
    "Release candidate tagging",
    "release candidate tag manifest",
    "PR evidence closeout",
    "PR closeout evidence checklist",
    "every manual release action has an accountable owner",
    "privacy/POPIA approval remains separate from technical approval",
    "rollback owner is assigned before release candidate tag creation",
    "post-deploy verification owner is assigned before deployment",
    "owner assignments must be recorded before manual approval",
    "does not grant approval, execute deployment, or create release tags",
    "make release-owner-accountability-check",
)


@dataclass(frozen=True)
class ReleaseOwnerAccountabilityResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseOwnerAccountabilityResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        ReleaseOwnerAccountabilityResult(DOC.exists(), "matrix present" if DOC.exists() else "matrix missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseOwnerAccountabilityResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Release owner accountability check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
