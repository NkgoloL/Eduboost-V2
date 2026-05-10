#!/usr/bin/env python3
"""Validate Cluster G frontend journey evidence baseline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "tests/unit/test_cluster_g_mocked_playwright_evidence.py",
    "tests/unit/test_frontend_playwright_mocked_specs.py",
    "tests/unit/test_frontend_playwright_mock_helpers.py",
    "docs/frontend/playwright_mocked_journey_specs.md",
    "docs/frontend/playwright_mock_route_helpers.md",
    "scripts/check_frontend_playwright_mocked_specs.py",
    "scripts/check_frontend_playwright_mock_helpers.py",
    "tests/e2e/parent-mocked-api-journey.spec.ts",
    "tests/e2e/learner-mocked-api-journey.spec.ts",
    "tests/e2e/support/mockApi.ts",
    "tests/unit/test_cluster_g_runtime_mock_evidence.py",
    "tests/unit/test_frontend_mock_api_fixtures.py",
    "tests/unit/test_frontend_runtime_inventory.py",
    "tests/fixtures/frontend/api/authorization_denied_error.json",
    "tests/fixtures/frontend/api/consent_denied_error.json",
    "tests/fixtures/frontend/api/parent_dashboard_success.json",
    "tests/fixtures/frontend/api/lesson_generation_success.json",
    "tests/fixtures/frontend/api/diagnostic_submit_success.json",
    "tests/fixtures/frontend/api/learner_dashboard_success.json",
    "docs/frontend/playwright_mock_api_fixtures.md",
    "docs/frontend/frontend_runtime_inventory.md",
    "scripts/check_frontend_mock_api_fixtures.py",
    "scripts/check_frontend_runtime_inventory.py",
    "scripts/generate_frontend_runtime_inventory.py",
    "tests/unit/test_cluster_g_accessibility_evidence.py",
    "tests/unit/test_frontend_accessibility_static.py",
    "tests/unit/test_frontend_accessibility_contract.py",
    "docs/frontend/frontend_accessibility_static_scan.md",
    "docs/frontend/frontend_accessibility_contract.md",
    "scripts/check_frontend_accessibility_static.py",
    "scripts/check_frontend_accessibility_contract.py",
    "tests/unit/test_cluster_g_playwright_evidence.py",
    "tests/unit/test_frontend_playwright_specs.py",
    "tests/unit/test_frontend_playwright_scaffold.py",
    "tests/e2e/parent-vertical-journey.spec.ts",
    "tests/e2e/learner-vertical-journey.spec.ts",
    "docs/frontend/playwright_vertical_journey_specs.md",
    "docs/frontend/playwright_e2e_scaffold.md",
    "scripts/check_frontend_playwright_specs.py",
    "scripts/check_frontend_playwright_scaffold.py",
    "playwright.config.ts",
    "tests/unit/test_cluster_g_api_fixture_evidence.py",
    "tests/unit/test_frontend_journey_fixtures.py",
    "tests/unit/test_frontend_api_client_inventory.py",
    "tests/fixtures/frontend/parent_journey_fixture.json",
    "tests/fixtures/frontend/learner_journey_fixture.json",
    "docs/frontend/playwright_journey_fixture_contract.md",
    "docs/frontend/frontend_api_client_inventory.md",
    "scripts/check_frontend_journey_fixtures.py",
    "scripts/check_frontend_api_client_inventory.py",
    "scripts/generate_frontend_api_client_inventory.py",
    "tests/unit/test_cluster_g_parent_denial_evidence.py",
    "tests/unit/test_frontend_auth_consent_denial_contract.py",
    "tests/unit/test_parent_vertical_journey_contract.py",
    "docs/frontend/frontend_auth_consent_denial_contract.md",
    "docs/frontend/parent_vertical_journey_contract.md",
    "scripts/check_frontend_auth_consent_denial_contract.py",
    "scripts/check_parent_vertical_journey_contract.py",
    "scripts/generate_frontend_route_inventory.py",
    "scripts/check_frontend_route_inventory.py",
    "scripts/check_learner_vertical_journey_contract.py",
    "docs/frontend/frontend_route_inventory.md",
    "docs/frontend/learner_vertical_journey_contract.md",
    "tests/unit/test_frontend_route_inventory.py",
    "tests/unit/test_learner_vertical_journey_contract.py",
)

CONTENT_REQUIREMENTS = {
    "docs/frontend/playwright_mocked_journey_specs.md": (
        "Playwright Mocked Journey Specs",
        "must not require live learner data",
    ),
    "docs/frontend/playwright_mock_route_helpers.md": (
        "Playwright Mock Route Helpers",
        "canonical API fixture envelopes",
    ),
    "docs/frontend/playwright_mock_api_fixtures.md": (
        "Playwright Mock API Fixtures",
        "error.safe_next_action",
    ),
    "docs/frontend/frontend_runtime_inventory.md": (
        "Frontend Runtime Inventory",
        "run Playwright E2E",
    ),
    "docs/frontend/frontend_accessibility_static_scan.md": (
        "Frontend Accessibility Static Scan",
        "source-level guard",
    ),
    "docs/frontend/frontend_accessibility_contract.md": (
        "Frontend Accessibility Contract",
        "keyboard navigation reaches primary learner and parent actions",
        "learner-facing copy remains age-appropriate",
    ),
    "docs/frontend/playwright_vertical_journey_specs.md": (
        "Playwright Vertical Journey Specs",
        "frontend shell is not blank",
    ),
    "docs/frontend/playwright_e2e_scaffold.md": (
        "Playwright E2E Scaffold",
        "runtime browser tests should run in a frontend or staging workflow",
    ),
    "docs/frontend/playwright_journey_fixture_contract.md": (
        "Playwright Journey Fixture Contract",
        "consent and authorization denial states",
    ),
    "docs/frontend/frontend_api_client_inventory.md": (
        "Frontend API Client Inventory",
        "error envelope parsing",
    ),
    "docs/frontend/frontend_auth_consent_denial_contract.md": (
        "Frontend Auth Consent Denial Contract",
        "denial states must show safe next action",
    ),
    "docs/frontend/parent_vertical_journey_contract.md": (
        "Parent Vertical Journey Contract",
        "does not expose unrelated learner data",
    ),
    "Makefile": (
        "frontend-route-inventory:",
        "frontend-route-inventory-check:",
        "learner-vertical-journey-contract-check:",
        "parent-vertical-journey-contract-check:",
        "frontend-auth-consent-denial-check:",
        "frontend-api-client-inventory:",
        "frontend-api-client-inventory-check:",
        "frontend-journey-fixture-check:",
        "frontend-playwright-scaffold-check:",
        "frontend-playwright-specs-check:",
        "frontend-e2e:",
        "frontend-accessibility-contract-check:",
        "frontend-accessibility-static-check:",
        "frontend-runtime-inventory:",
        "frontend-runtime-inventory-check:",
        "frontend-mock-api-fixture-check:",
        "frontend-playwright-mock-helper-check:",
        "frontend-playwright-mocked-specs-check:",
    ),
    "docs/frontend/frontend_route_inventory.md": (
        "Frontend Route Inventory",
        "Required Journey Areas",
    ),
    "docs/frontend/learner_vertical_journey_contract.md": (
        "Learner Vertical Journey Contract",
        "learner sees progress/mastery feedback",
    ),
}


@dataclass(frozen=True)
class ClusterGResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterGResult]:
    results: list[ClusterGResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(ClusterGResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                ClusterGResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster G frontend evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
