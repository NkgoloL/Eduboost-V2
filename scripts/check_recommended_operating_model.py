#!/usr/bin/env python3
"""Validate the recommended operating model contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "recommended_operating_model.md"

REQUIRED_SNIPPETS = (
    "Recommended Operating Model",
    "execution contract",
    "does not make the project release-ready",
    "Single Source Of Truth",
    "docs/current_state.md",
    "docs/project_status.md",
    "TODO.md",
    "docs/repository_governance.md",
    "docs/release/EVIDENCE_INDEX.md",
    "Do not claim release-ready, public-beta-ready, or production-ready status",
    "Evidence-First Delivery",
    "Repository-side implementation is not the same as CI, staging, legal",
    "Use the status vocabulary from `TODO.md`",
    "Protected Change Flow",
    "Open a PR with the repository PR template completed",
    "make runtime-check",
    "make openapi-check",
    "make route-inventory-check",
    "make verify-repo-state",
    "make recommended-operating-model-check",
    "Release Control",
    "Release work is gated by evidence, not by intent",
    "Complete the release-owner go/no-go decision before tagging",
    "Operating Cadence And Accountability",
    "Technical approval, privacy/POPIA approval, rollback ownership",
    "External approvals stay `[external]`",
    "not a release go/no-go decision",
)


@dataclass(frozen=True)
class RecommendedOperatingModelResult:
    ok: bool
    detail: str


def run_checks() -> list[RecommendedOperatingModelResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        RecommendedOperatingModelResult(
            DOC.exists(),
            "operating model present" if DOC.exists() else "operating model missing",
        )
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            RecommendedOperatingModelResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Recommended operating model check")
    print("Scope: documentation contract only; not a release go/no-go decision")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
