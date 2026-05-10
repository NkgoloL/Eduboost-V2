#!/usr/bin/env python3
"""Validate the staging release gate documentation and artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "staging_release_gate.md"

REQUIRED_SNIPPETS = (
    "make runtime-check",
    "make openapi-check",
    "make route-inventory-check",
    "make pr002r-check",
    "make phase2-authz-closure",
    "make popia-consent-closure-check",
    "make cluster-d-closure-check",
    "python3 scripts/generate_release_evidence_manifest.py",
    "Production promotion is blocked",
)

REQUIRED_ARTIFACTS = (
    "docs/operations/release_evidence_manifest.md",
    "docs/operations/deployment_readiness_checklist.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/security/PHASE2_AUTHORIZATION_CLOSURE.md",
    "docs/openapi.json",
    "docs/route_inventory.md",
)


@dataclass(frozen=True)
class StagingGateResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[StagingGateResult]:
    results: list[StagingGateResult] = []
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""

    results.append(StagingGateResult("file", str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "present" if DOC.exists() else "missing"))

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            StagingGateResult(
                "content",
                str(DOC.relative_to(REPO_ROOT)),
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    for rel_path in REQUIRED_ARTIFACTS:
        path = REPO_ROOT / rel_path
        results.append(
            StagingGateResult(
                "artifact",
                rel_path,
                path.exists(),
                "present" if path.exists() else "missing",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Staging release gate check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
