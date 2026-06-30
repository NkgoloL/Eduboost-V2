#!/usr/bin/env python3
"""Validate frontend route inventory evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_route_inventory.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_frontend_route_inventory.py"

REQUIRED_SNIPPETS = (
    "Frontend Route Inventory",
    "Required Journey Areas",
    "learner onboarding",
    "learner dashboard",
    "diagnostic start and submit",
    "lesson generation and lesson view",
    "parent dashboard and learner progress",
    "consent and trust surfaces",
    "make frontend-route-inventory",
)


@dataclass(frozen=True)
class FrontendInventoryResult:
    ok: bool
    detail: str


def run_checks() -> list[FrontendInventoryResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""

    results = [
        FrontendInventoryResult(DOC.exists(), "inventory present" if DOC.exists() else "inventory missing"),
        FrontendInventoryResult("JOURNEY_MARKERS" in generator_text, "generator defines journey markers" if "JOURNEY_MARKERS" in generator_text else "generator missing journey markers"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FrontendInventoryResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend route inventory check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
