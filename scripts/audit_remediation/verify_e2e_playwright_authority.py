#!/usr/bin/env python3
"""Verify TA Phase 06 Playwright/E2E authority configuration."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Finding:
    valid: bool
    message: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify() -> dict[str, object]:
    root_pkg = REPO_ROOT / "package.json"
    frontend_pkg = REPO_ROOT / "app/frontend/package.json"
    root_lock = REPO_ROOT / "pnpm-lock.yaml"
    frontend_lock = REPO_ROOT / "app/frontend/pnpm-lock.yaml"
    playwright_config = _read(REPO_ROOT / "playwright.config.ts")
    ci_cd = _read(REPO_ROOT / ".github/workflows/ci-cd.yml")
    e2e = _read(REPO_ROOT / ".github/workflows/e2e.yml")
    frontend_e2e = _read(REPO_ROOT / ".github/workflows/frontend-e2e.yml")
    blocker_register = _read(REPO_ROOT / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json")

    findings: list[Finding] = []
    findings.append(Finding(root_pkg.exists(), "root package.json exists" if root_pkg.exists() else "root package.json missing"))
    findings.append(Finding(frontend_pkg.exists(), "frontend package.json exists" if frontend_pkg.exists() else "frontend package.json missing"))
    findings.append(Finding(root_lock.exists(), "root pnpm lockfile exists" if root_lock.exists() else "root pnpm lockfile missing"))
    findings.append(Finding(frontend_lock.exists(), "frontend pnpm lockfile exists" if frontend_lock.exists() else "frontend pnpm lockfile missing"))

    if root_pkg.exists():
        root_payload = _json(root_pkg)
        dev_deps = root_payload.get("devDependencies", {})
        findings.append(Finding(str(root_payload.get("packageManager", "")).startswith("pnpm@"), "root package manager is pnpm"))
        findings.append(Finding("@playwright/test" in dev_deps, "root @playwright/test dependency declared"))
    if frontend_pkg.exists():
        frontend_payload = _json(frontend_pkg)
        findings.append(Finding(str(frontend_payload.get("packageManager", "")).startswith("pnpm@"), "frontend package manager is pnpm"))

    findings.append(Finding('"http://127.0.0.1:3050"' in playwright_config, "Playwright default base URL uses Next.js port 3050"))
    findings.append(Finding("pnpm --dir app/frontend exec next dev" in playwright_config, "Playwright webServer starts frontend through pnpm"))
    findings.append(Finding("testDir: \"./tests/e2e\"" in playwright_config, "Playwright testDir is tests/e2e"))
    findings.append(Finding("playwright-report" in playwright_config and "test-results" in playwright_config, "Playwright report/result directories are configured"))

    required_specs = [
        "tests/e2e/learner-mocked-api-journey.spec.ts",
        "tests/e2e/parent-mocked-api-journey.spec.ts",
    ]
    for spec in required_specs:
        findings.append(Finding((REPO_ROOT / spec).exists(), f"required mocked E2E spec exists: {spec}"))

    all_workflows = "\n---ci-cd---\n" + ci_cd + "\n---e2e---\n" + e2e + "\n---frontend-e2e---\n" + frontend_e2e
    for forbidden in ("npm ci", "npx playwright", "app/frontend/node_modules/.bin/playwright", "actions/setup-node@v6"):
        findings.append(Finding(forbidden not in all_workflows, f"workflow does not use forbidden E2E pattern: {forbidden}"))
    for required in (
        "pnpm install --frozen-lockfile",
        "pnpm --dir app/frontend install --frozen-lockfile",
        "pnpm exec playwright install --with-deps chromium",
        "pnpm exec playwright test",
        "actions/upload-artifact@v4",
        "test-results/",
        "playwright-report/",
    ):
        findings.append(Finding(required in all_workflows, f"workflow contains required E2E snippet: {required}"))

    # Ensure workflows cache both lockfiles where E2E installs root and frontend dependencies.
    for name, text in (("ci-cd.yml", ci_cd), ("e2e.yml", e2e), ("frontend-e2e.yml", frontend_e2e)):
        if "playwright" in text.lower():
            findings.append(Finding("pnpm-lock.yaml" in text and "app/frontend/pnpm-lock.yaml" in text, f"{name} caches root and frontend pnpm lockfiles"))

    findings.append(Finding("TA-E2E-001" in blocker_register, "TA-E2E-001 blocker registered"))
    terminal_closed = (
        "technical-audit-remediation-closed" in blocker_register
        or "technical-audit-post-merge-baseline-recorded" in blocker_register
    )
    phase_active = "06-e2e-playwright-execution-authority" in blocker_register
    findings.append(Finding(phase_active or terminal_closed, "Phase 06 active or archived terminal slice registered"))

    return {
        "valid": all(f.valid for f in findings),
        "authority_scope": "mocked_frontend_playwright_journeys",
        "remote_ci_run_claimed": False,
        "full_backend_backed_e2e_claimed": False,
        "findings": [asdict(f) for f in findings],
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = verify()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for finding in payload["findings"]:
            print(f"{'PASS' if finding['valid'] else 'FAIL'} {finding['message']}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
