#!/usr/bin/env python3
"""Validate staging smoke evidence manifest."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "staging_smoke_evidence_manifest.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_staging_smoke_evidence_manifest.py"

REQUIRED_SNIPPETS = (
    "Staging Smoke Evidence Manifest",
    "runtime import smoke",
    "OpenAPI drift smoke",
    "staging release gate",
    "release evidence artifacts",
    "Cluster D deployment closure",
    "Cluster E data resilience closure",
    "Cluster F AI safety closure",
    "Cluster G frontend journey closure",
    "make staging-smoke-evidence-manifest",
)

GENERATOR_SNIPPETS = (
    "SMOKE_CHECKS",
    "cluster-g-closure-check",
    "release-evidence-artifacts-check",
)


@dataclass(frozen=True)
class StagingSmokeManifestResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[StagingSmokeManifestResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    results = [
        StagingSmokeManifestResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "manifest present" if DOC.exists() else "manifest missing"),
        StagingSmokeManifestResult(str(GENERATOR.relative_to(REPO_ROOT)), GENERATOR.exists(), "generator present" if GENERATOR.exists() else "generator missing"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            StagingSmokeManifestResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in GENERATOR_SNIPPETS:
        results.append(
            StagingSmokeManifestResult(
                str(GENERATOR.relative_to(REPO_ROOT)),
                snippet in generator_text,
                f"contains {snippet!r}" if snippet in generator_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Staging smoke evidence manifest check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
