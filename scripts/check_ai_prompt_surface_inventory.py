#!/usr/bin/env python3
"""Validate AI prompt surface inventory evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "ai_prompt_surface_inventory.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_ai_prompt_surface_inventory.py"

REQUIRED_SNIPPETS = (
    "AI Prompt Surface Inventory",
    "Required Safety Markers",
    "CAPS alignment",
    "consent-authorized learner context",
    "AI safety boundary instructions",
    "no cross-learner data leakage",
    "Discovered Surfaces",
)


@dataclass(frozen=True)
class PromptSurfaceInventoryResult:
    ok: bool
    detail: str


def run_checks() -> list[PromptSurfaceInventoryResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    results = [
        PromptSurfaceInventoryResult(DOC.exists(), "inventory present" if DOC.exists() else "inventory missing"),
        PromptSurfaceInventoryResult("PROMPT_MARKERS" in generator_text, "generator defines prompt markers" if "PROMPT_MARKERS" in generator_text else "generator missing prompt markers"),
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PromptSurfaceInventoryResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("AI prompt surface inventory check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
