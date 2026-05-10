#!/usr/bin/env python3
"""Validate frontend API client inventory evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_api_client_inventory.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_frontend_api_client_inventory.py"

REQUIRED_SNIPPETS = (
    "Frontend API Client Inventory",
    "Required API Domains",
    "learner-scoped reads",
    "learner-scoped writes",
    "parent-scoped reads",
    "consent status and consent mutation",
    "diagnostic start and submit",
    "lesson generation and lesson retrieval",
    "error envelope parsing",
    "make frontend-api-client-inventory",
)


@dataclass(frozen=True)
class FrontendApiInventoryResult:
    ok: bool
    detail: str


def run_checks() -> list[FrontendApiInventoryResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""

    results = [
        FrontendApiInventoryResult(DOC.exists(), "inventory present" if DOC.exists() else "inventory missing"),
        FrontendApiInventoryResult("API_MARKERS" in generator_text, "generator defines API markers" if "API_MARKERS" in generator_text else "generator missing API markers"),
        FrontendApiInventoryResult("DOMAIN_MARKERS" in generator_text, "generator defines domain markers" if "DOMAIN_MARKERS" in generator_text else "generator missing domain markers"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FrontendApiInventoryResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend API client inventory check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
