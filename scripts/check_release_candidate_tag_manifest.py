#!/usr/bin/env python3
"""Validate release candidate tag manifest."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_candidate_tag_manifest.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_release_candidate_tag_manifest.py"

REQUIRED_SNIPPETS = (
    "Release Candidate Tag Manifest",
    "beta release candidate tag format",
    "release tags must point to reviewed commits",
    "release tags must be paired with beta release evidence bundle",
    "release tags must be paired with beta sign-off manifest",
    "rollback owner assignment",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/beta_signoff_manifest.md",
    "docs/operations/staging_smoke_evidence_manifest.md",
    "git tag -a",
    "git push origin",
    "Do not create or push the release tag until Cluster H checks pass",
    "make release-candidate-tag-manifest",
)

GENERATOR_SNIPPETS = (
    "RELEASE_CANDIDATE",
    "beta-<short-sha>",
    "generate_release_candidate_tag_manifest",
)


@dataclass(frozen=True)
class ReleaseCandidateTagResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ReleaseCandidateTagResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    results = [
        ReleaseCandidateTagResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "manifest present" if DOC.exists() else "manifest missing"),
        ReleaseCandidateTagResult(str(GENERATOR.relative_to(REPO_ROOT)), GENERATOR.exists(), "generator present" if GENERATOR.exists() else "generator missing"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseCandidateTagResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in GENERATOR_SNIPPETS:
        results.append(
            ReleaseCandidateTagResult(
                str(GENERATOR.relative_to(REPO_ROOT)),
                snippet in generator_text,
                f"contains {snippet!r}" if snippet in generator_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Release candidate tag manifest check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
