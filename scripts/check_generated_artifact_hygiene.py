#!/usr/bin/env python3
"""Validate generated artifact hygiene evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "generated_artifact_hygiene_contract.md"
GITIGNORE = REPO_ROOT / ".gitignore"

DOC_SNIPPETS = (
    "Generated Artifact Hygiene Contract",
    "Generated Artifacts Excluded From Release Evidence",
    "`coverage.xml`",
    "generated coverage output is not release evidence",
    "coverage.xml conflicts must be resolved by removal, not manual merge",
    "release commits must include only source, docs, workflow, and test evidence",
    "force-push is not the default recovery path",
    "make generated-artifact-hygiene-check",
)

GITIGNORE_SNIPPETS = (
    "coverage.xml",
    ".coverage",
    ".pytest_cache/",
    ".hypothesis/",
    "htmlcov/",
    "playwright-report/",
    "test-results/",
)


@dataclass(frozen=True)
class GeneratedArtifactHygieneResult:
    target: str
    ok: bool
    detail: str


def _normalize_gitignore(text: str) -> set[str]:
    return {line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")}


def run_checks() -> list[GeneratedArtifactHygieneResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    gitignore_text = GITIGNORE.read_text(encoding="utf-8") if GITIGNORE.exists() else ""
    gitignore_lines = _normalize_gitignore(gitignore_text)

    results = [
        GeneratedArtifactHygieneResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "contract present" if DOC.exists() else "contract missing"),
        GeneratedArtifactHygieneResult(str(GITIGNORE.relative_to(REPO_ROOT)), GITIGNORE.exists(), "gitignore present" if GITIGNORE.exists() else "gitignore missing"),
    ]

    for snippet in DOC_SNIPPETS:
        results.append(
            GeneratedArtifactHygieneResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in GITIGNORE_SNIPPETS:
        results.append(
            GeneratedArtifactHygieneResult(
                str(GITIGNORE.relative_to(REPO_ROOT)),
                snippet in gitignore_lines,
                f"contains {snippet!r}" if snippet in gitignore_lines else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Generated artifact hygiene check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
