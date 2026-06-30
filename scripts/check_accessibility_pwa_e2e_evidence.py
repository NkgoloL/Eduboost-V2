#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "app/frontend/src/components/accessibility/A11y.tsx",
    "app/frontend/public/manifest.json",
    "app/frontend/public/service-worker.js",
    "app/frontend/src/lib/api/offlineSync.ts",
    "docs/frontend/frontend_accessibility_contract.md",
    "docs/frontend/frontend_accessibility_static_scan.md",
    "docs/frontend/frontend_e2e_environment_contract.md",
    "docs/frontend/frontend_e2e_opt_in_workflow.md",
    "docs/frontend/playwright_e2e_scaffold.md",
    "tests/e2e/learner-vertical-journey.spec.ts",
    "tests/e2e/parent-vertical-journey.spec.ts",
    "app/frontend/src/__tests__/AccessibilityContracts.test.tsx",
    "app/frontend/src/__tests__/OfflineSync.test.ts",
)


@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def check_all() -> list[Result]:
    return [Result(p, (ROOT / p).exists(), "present" if (ROOT / p).exists() else "missing") for p in REQUIRED]


def main() -> int:
    results = check_all()
    print("Accessibility/PWA/E2E evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
