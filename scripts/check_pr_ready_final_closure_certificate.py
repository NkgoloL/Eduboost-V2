#!/usr/bin/env python3
"""Validate PR-ready final closure certificate."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "pr_ready_final_closure_certificate.md"

REQUIRED_SNIPPETS = (
    "PR-Ready Final Closure Certificate",
    "archival lock assertion is present",
    "final acceptance packet index is present",
    "release handoff freeze assertion is present",
    "final release evidence ledger is present",
    "final merge signoff lock is present",
    "release owner post-closeout decision record is present",
    "final evidence no-op execution assertion is present",
    "final project closeout attestation is present",
    "Cluster H release evidence checksum index is present",
    "post-closeout evidence access policy is present",
    "Certificate ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Reviewer",
    "Certificate Time UTC",
    "Certificate Outcome",
    "certificate must reference release candidate and commit SHA",
    "certificate must reference branch and PR number",
    "certificate must preserve no-op execution boundary",
    "certificate must preserve manual approval workflow references",
    "certificate must preserve final acceptance packet references",
    "certificate must preserve archival lock references",
    "certificate must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make pr-ready-final-closure-certificate-check",
)


@dataclass(frozen=True)
class PrReadyFinalClosureCertificateResult:
    ok: bool
    detail: str


def run_checks() -> list[PrReadyFinalClosureCertificateResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [PrReadyFinalClosureCertificateResult(DOC.exists(), "certificate present" if DOC.exists() else "certificate missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PrReadyFinalClosureCertificateResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("PR-ready final closure certificate check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
