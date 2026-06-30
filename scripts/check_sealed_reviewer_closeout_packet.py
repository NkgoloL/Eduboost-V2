#!/usr/bin/env python3
"""Validate sealed reviewer closeout packet."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "sealed_reviewer_closeout_packet.md"

REQUIRED_SNIPPETS = (
    "Sealed Reviewer Closeout Packet",
    "final release operator brief",
    "terminal review index",
    "sealed evidence access handoff",
    "terminal evidence seal",
    "final PR handoff summary",
    "final reviewer disposition record",
    "final closure manifest",
    "branch handoff proof record",
    "reviewer decision capture template",
    "post-closeout evidence access policy",
    "Packet ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Reviewer",
    "Packet Time UTC",
    "Packet Outcome",
    "Evidence Archive Location",
    "packet must reference release candidate and commit SHA",
    "packet must reference branch and PR number",
    "packet must preserve terminal evidence seal references",
    "packet must preserve terminal review index references",
    "packet must preserve sealed evidence access handoff references",
    "packet must preserve final reviewer disposition record references",
    "packet must preserve no-op execution boundary references",
    "packet must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make sealed-reviewer-closeout-packet-check",
)


@dataclass(frozen=True)
class SealedReviewerCloseoutPacketResult:
    ok: bool
    detail: str


def run_checks() -> list[SealedReviewerCloseoutPacketResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [SealedReviewerCloseoutPacketResult(DOC.exists(), "packet present" if DOC.exists() else "packet missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            SealedReviewerCloseoutPacketResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Sealed reviewer closeout packet check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
