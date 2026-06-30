#!/usr/bin/env python3
"""Validate terminal handoff closure note."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "terminal_handoff_closure_note.md"

REQUIRED_SNIPPETS = (
    "Terminal Handoff Closure Note",
    "final sealed package manifest",
    "audit review closeout certificate",
    "sealed reviewer closeout packet",
    "final audit handoff register",
    "terminal PR evidence index",
    "final release operator brief",
    "terminal review index",
    "sealed evidence access handoff",
    "terminal evidence seal",
    "final PR handoff summary",
    "Closure Note ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Closing Owner",
    "Closure Time UTC",
    "Closure Outcome",
    "Evidence Archive Location",
    "terminal handoff must reference release candidate and commit SHA",
    "terminal handoff must reference branch and PR number",
    "terminal handoff must preserve final sealed package manifest references",
    "terminal handoff must preserve audit review closeout certificate references",
    "terminal handoff must preserve sealed reviewer closeout packet references",
    "terminal handoff must preserve terminal PR evidence index references",
    "terminal handoff must preserve no-op execution boundary references",
    "terminal handoff must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make terminal-handoff-closure-note-check",
)


@dataclass(frozen=True)
class TerminalHandoffClosureNoteResult:
    ok: bool
    detail: str


def run_checks() -> list[TerminalHandoffClosureNoteResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [TerminalHandoffClosureNoteResult(DOC.exists(), "note present" if DOC.exists() else "note missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            TerminalHandoffClosureNoteResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Terminal handoff closure note check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
