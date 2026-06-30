#!/usr/bin/env python3
"""Validate remediation safety evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "remediation_safety_contract.md"

REQUIRED_SNIPPETS = (
    "Remediation Safety Contract",
    "observed learner gap",
    "learner mastery state",
    "remediation objective",
    "consent-authorized learner identifier",
    "safety boundary instructions",
    "remediation must remain educational",
    "remediation must not label the learner with unsupported diagnoses",
    "remediation must avoid unsafe instructions",
    "remediation must not include sexual content",
    "remediation must not include self-harm content",
    "remediation must not expose another learner's data",
    "remediation must map to the observed learner gap",
    "remediation must preserve CAPS alignment",
    "remediation must avoid punitive or shaming language",
    "make remediation-safety-contract-check",
)


@dataclass(frozen=True)
class RemediationSafetyResult:
    ok: bool
    detail: str


def run_checks() -> list[RemediationSafetyResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [RemediationSafetyResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            RemediationSafetyResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Remediation safety contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
