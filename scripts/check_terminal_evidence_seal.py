#!/usr/bin/env python3
"""Validate terminal evidence seal."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "terminal_evidence_seal.md"

REQUIRED_SNIPPETS = (
    "Terminal Evidence Seal",
    "final reviewer disposition record",
    "reviewer decision capture template",
    "final closure manifest",
    "branch handoff proof record",
    "final acceptance memo",
    "release record closure ledger",
    "post-merge evidence continuity note",
    "final release evidence table of contents",
    "archival lock assertion",
    "evidence freeze confirmation record",
    "Seal ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Sealed By",
    "Sealed At UTC",
    "Seal Outcome",
    "Evidence Archive Location",
    "seal must reference release candidate and commit SHA",
    "seal must reference branch and PR number",
    "seal must preserve final reviewer disposition record references",
    "seal must preserve final closure manifest references",
    "seal must preserve evidence freeze confirmation record references",
    "seal must preserve archival lock assertion references",
    "seal must preserve no-op execution boundary references",
    "seal must remain controlled staging/beta evidence",
    "seal does not approve production launch",
    "seal does not execute deployment",
    "seal does not create release tags",
    "seal does not merge the pull request automatically",
    "seal does not bypass manual approval",
    "seal does not rewrite source control history",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make terminal-evidence-seal-check",
)


@dataclass(frozen=True)
class TerminalEvidenceSealResult:
    ok: bool
    detail: str


def run_checks() -> list[TerminalEvidenceSealResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [TerminalEvidenceSealResult(DOC.exists(), "seal present" if DOC.exists() else "seal missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            TerminalEvidenceSealResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Terminal evidence seal check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
