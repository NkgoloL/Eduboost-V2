#!/usr/bin/env python3
"""Validate final sealed package manifest."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_sealed_package_manifest.md"

REQUIRED_SNIPPETS = (
    "Final Sealed Package Manifest",
    "sealed reviewer closeout packet",
    "final audit handoff register",
    "terminal PR evidence index",
    "final release operator brief",
    "terminal review index",
    "sealed evidence access handoff",
    "terminal evidence seal",
    "final PR handoff summary",
    "final reviewer disposition record",
    "final closure manifest",
    "Package Manifest ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Package Owner",
    "Manifest Time UTC",
    "Package Outcome",
    "Evidence Archive Location",
    "package manifest must reference release candidate and commit SHA",
    "package manifest must reference branch and PR number",
    "package manifest must preserve sealed reviewer closeout packet references",
    "package manifest must preserve final audit handoff register references",
    "package manifest must preserve terminal PR evidence index references",
    "package manifest must preserve no-op execution boundary references",
    "package manifest must preserve controlled staging/beta scope",
    "package manifest must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-sealed-package-manifest-check",
)


@dataclass(frozen=True)
class FinalSealedPackageManifestResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalSealedPackageManifestResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalSealedPackageManifestResult(DOC.exists(), "manifest present" if DOC.exists() else "manifest missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalSealedPackageManifestResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final sealed package manifest check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
