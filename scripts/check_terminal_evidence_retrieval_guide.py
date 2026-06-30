#!/usr/bin/env python3
"""Validate terminal evidence retrieval guide."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "terminal_evidence_retrieval_guide.md"

REQUIRED_SNIPPETS = (
    "Terminal Evidence Retrieval Guide",
    "final archive accession record",
    "post-closeout custody register",
    "final sealed package manifest",
    "audit review closeout certificate",
    "terminal handoff closure note",
    "terminal PR evidence index",
    "final release evidence table of contents",
    "post-closeout evidence access policy",
    "release evidence retention finalization",
    "cluster h release evidence checksum index",
    "Confirm release candidate and commit SHA.",
    "Confirm branch and PR number.",
    "Open the final archive accession record.",
    "Verify post-closeout custody register.",
    "Open the final sealed package manifest.",
    "Use terminal PR evidence index for PR evidence navigation.",
    "Use final release evidence table of contents for full evidence navigation.",
    "Verify checksum and ledger references.",
    "Apply post-closeout evidence access policy.",
    "Avoid unnecessary learner personal information.",
    "retrieval guide must reference release candidate and commit SHA",
    "retrieval guide must reference branch and PR number",
    "retrieval guide must preserve post-closeout evidence access policy references",
    "retrieval guide must preserve custody register references",
    "retrieval guide must preserve archive accession references",
    "retrieval guide must preserve checksum and ledger references",
    "retrieval guide must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make terminal-evidence-retrieval-guide-check",
)


@dataclass(frozen=True)
class TerminalEvidenceRetrievalGuideResult:
    ok: bool
    detail: str


def run_checks() -> list[TerminalEvidenceRetrievalGuideResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [TerminalEvidenceRetrievalGuideResult(DOC.exists(), "guide present" if DOC.exists() else "guide missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            TerminalEvidenceRetrievalGuideResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Terminal evidence retrieval guide check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
