#!/usr/bin/env python3
"""Validate post-merge evidence continuity note."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "post_merge_evidence_continuity_note.md"

REQUIRED_SNIPPETS = (
    "Post-Merge Evidence Continuity Note",
    "release record closure ledger",
    "final acceptance memo",
    "PR merge evidence summary",
    "evidence freeze confirmation record",
    "release evidence retention finalization",
    "final release evidence table of contents",
    "post-closeout evidence access policy",
    "final release evidence ledger",
    "frozen scope variance register",
    "post-closeout maintenance boundary",
    "continuity note must reference release candidate and commit SHA",
    "continuity note must reference branch and PR number",
    "continuity note must preserve source control history references",
    "continuity note must preserve final release evidence table of contents",
    "continuity note must preserve post-closeout evidence access policy",
    "continuity note must preserve frozen scope variance register",
    "continuity note must preserve no-op execution boundary",
    "continuity note must not authorize unrestricted production launch",
    "no deployment is executed by this note",
    "no release tag is created by this note",
    "no production approval is granted by this note",
    "no manual approval is replaced by this note",
    "no audit evidence is deleted by this note",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make post-merge-evidence-continuity-note-check",
)


@dataclass(frozen=True)
class PostMergeEvidenceContinuityNoteResult:
    ok: bool
    detail: str


def run_checks() -> list[PostMergeEvidenceContinuityNoteResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [PostMergeEvidenceContinuityNoteResult(DOC.exists(), "note present" if DOC.exists() else "note missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PostMergeEvidenceContinuityNoteResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Post-merge evidence continuity note check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
