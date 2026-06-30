#!/usr/bin/env python3
"""Validate AI prompt input evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "ai_prompt_input_contract.md"

REQUIRED_SNIPPETS = (
    "AI Prompt Input Contract",
    "learner grade",
    "learner subject",
    "CAPS strand or skill",
    "learner mastery state",
    "consent-authorized learner identifier",
    "safety boundary instructions",
    "raw secrets",
    "API keys",
    "another learner's diagnostic history",
    "prompts must preserve CAPS alignment",
    "prompts must avoid cross-learner data leakage",
    "make ai-prompt-input-contract-check",
)


@dataclass(frozen=True)
class PromptInputResult:
    ok: bool
    detail: str


def run_checks() -> list[PromptInputResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [PromptInputResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PromptInputResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("AI prompt input contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
