#!/usr/bin/env python3
"""Validate the release-candidate evidence sweep document."""
from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_candidate_evidence_sweep_2026-05-11.md"

REQUIRED_SNIPPETS = (
    "Release Candidate Evidence Sweep",
    "codex/pr17-rc-evidence-sweep",
    "make runtime-check openapi-check route-inventory-check beta-release-readiness-contract-check diagnostics-assessment-check",
    "make migration-check",
    "python3 -m pytest tests/smoke tests/test_entrypoints.py tests/test_health_checks.py -q --no-cov",
    "35 passed",
    "4 skipped",
    "make popia-consent-gate-check",
    "New unallowlisted missing markers: 103",
    "does not make EduBoost V2 public-beta-ready or production-ready",
)


def main() -> int:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    print("Release-candidate evidence sweep check")

    if not DOC.exists():
        print(f"- FAIL {DOC.relative_to(REPO_ROOT)}: document missing")
        return 1

    failed = False
    print(f"- PASS {DOC.relative_to(REPO_ROOT)}: document present")
    for snippet in REQUIRED_SNIPPETS:
        if snippet in text:
            print(f"- PASS contains {snippet!r}")
            continue
        print(f"- FAIL missing {snippet!r}")
        failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
