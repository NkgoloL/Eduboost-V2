#!/usr/bin/env python3
"""Validate frontend Playwright scaffold evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "playwright.config.ts"
DOC = REPO_ROOT / "docs" / "frontend" / "playwright_e2e_scaffold.md"

REQUIRED_CONFIG_SNIPPETS = (
    "defineConfig",
    "testDir: \"./tests/e2e\"",
    "FRONTEND_BASE_URL",
    "PLAYWRIGHT_WEB_SERVER_COMMAND",
    "Desktop Chrome",
)

REQUIRED_DOC_SNIPPETS = (
    "Playwright E2E Scaffold",
    "frontend vertical",
    "make frontend-playwright-scaffold-check",
    "make frontend-e2e",
    "runtime browser tests should run in a frontend or staging workflow",
)


@dataclass(frozen=True)
class PlaywrightScaffoldResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[PlaywrightScaffoldResult]:
    results: list[PlaywrightScaffoldResult] = []
    config_text = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""

    results.append(
        PlaywrightScaffoldResult(str(CONFIG.relative_to(REPO_ROOT)), CONFIG.exists(), "config present" if CONFIG.exists() else "config missing")
    )
    results.append(
        PlaywrightScaffoldResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "doc present" if DOC.exists() else "doc missing")
    )

    for snippet in REQUIRED_CONFIG_SNIPPETS:
        results.append(
            PlaywrightScaffoldResult(
                str(CONFIG.relative_to(REPO_ROOT)),
                snippet in config_text,
                f"contains {snippet!r}" if snippet in config_text else f"missing {snippet!r}",
            )
        )

    for snippet in REQUIRED_DOC_SNIPPETS:
        results.append(
            PlaywrightScaffoldResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend Playwright scaffold check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
