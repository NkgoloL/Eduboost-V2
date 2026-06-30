#!/usr/bin/env python3
"""Validate frontend runtime inventory evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_runtime_inventory.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_frontend_runtime_inventory.py"

REQUIRED_SNIPPETS = (
    "Frontend Runtime Inventory",
    "Package Manager",
    "Required Command Areas",
    "install dependencies",
    "start development server",
    "build frontend",
    "run frontend unit tests",
    "run Playwright E2E",
    "run accessibility scaffold",
    "make frontend-e2e",
)


@dataclass(frozen=True)
class FrontendRuntimeInventoryResult:
    ok: bool
    detail: str


def run_checks() -> list[FrontendRuntimeInventoryResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""

    results = [
        FrontendRuntimeInventoryResult(DOC.exists(), "inventory present" if DOC.exists() else "inventory missing"),
        FrontendRuntimeInventoryResult("PACKAGE_CANDIDATES" in generator_text, "generator checks package candidates" if "PACKAGE_CANDIDATES" in generator_text else "generator missing package candidates"),
        FrontendRuntimeInventoryResult("REQUIRED_COMMAND_AREAS" in generator_text, "generator defines command areas" if "REQUIRED_COMMAND_AREAS" in generator_text else "generator missing command areas"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FrontendRuntimeInventoryResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend runtime inventory check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
