#!/usr/bin/env python3
"""Validate release handoff freeze assertion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_handoff_freeze_assertion.md"

REQUIRED_SNIPPETS = (
    "Release Handoff Freeze Assertion",
    "final acceptance packet index is present",
    "final release evidence ledger is present",
    "frozen scope variance register is present",
    "post-closeout maintenance boundary is present",
    "final release handoff package is present",
    "release owner post-closeout decision record is present",
    "final merge signoff lock is present",
    "final evidence no-op execution assertion is present",
    "Cluster H release evidence checksum index is present",
    "final project closeout attestation is present",
    "freeze must reference release candidate and commit SHA",
    "freeze must preserve final acceptance packet references",
    "freeze must preserve final release evidence ledger references",
    "freeze must route post-freeze changes through frozen scope variance register",
    "freeze must preserve post-closeout maintenance boundary",
    "freeze must preserve no-op execution boundary",
    "freeze must not authorize unrestricted production launch",
    "no deployment is executed by this freeze assertion",
    "no release tag is created by this freeze assertion",
    "no production approval is granted by this freeze assertion",
    "no manual approval is replaced by this freeze assertion",
    "no unresolved blocker issue is overridden by this freeze assertion",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make release-handoff-freeze-assertion-check",
)


@dataclass(frozen=True)
class ReleaseHandoffFreezeAssertionResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseHandoffFreezeAssertionResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ReleaseHandoffFreezeAssertionResult(DOC.exists(), "assertion present" if DOC.exists() else "assertion missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseHandoffFreezeAssertionResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Release handoff freeze assertion check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
