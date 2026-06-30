#!/usr/bin/env python3
"""Validate beta release sign-off manifest evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_signoff_manifest.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_beta_signoff_manifest.py"

REQUIRED_SNIPPETS = (
    "Beta Sign-Off Manifest",
    "technical lead sign-off",
    "privacy/POPIA sign-off",
    "data resilience sign-off",
    "AI safety sign-off",
    "frontend journey sign-off",
    "rollback owner sign-off",
    "docs/operations/beta_release_readiness_contract.md",
    "docs/operations/staging_smoke_evidence_manifest.md",
    "docs/frontend/CLUSTER_G_CLOSURE.md",
    "valid only for the referenced commit and release candidate",
    "make beta-signoff-manifest",
)

GENERATOR_SNIPPETS = (
    "SIGNOFF_AREAS",
    "REQUIRED_INPUTS",
    "RELEASE_CANDIDATE",
)


@dataclass(frozen=True)
class BetaSignoffManifestResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[BetaSignoffManifestResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    results = [
        BetaSignoffManifestResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "manifest present" if DOC.exists() else "manifest missing"),
        BetaSignoffManifestResult(str(GENERATOR.relative_to(REPO_ROOT)), GENERATOR.exists(), "generator present" if GENERATOR.exists() else "generator missing"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaSignoffManifestResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in GENERATOR_SNIPPETS:
        results.append(
            BetaSignoffManifestResult(
                str(GENERATOR.relative_to(REPO_ROOT)),
                snippet in generator_text,
                f"contains {snippet!r}" if snippet in generator_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Beta sign-off manifest check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
