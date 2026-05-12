"""
tests/unit/test_frontend_e2e_opt_in_workflow.py
================================================
Contract tests for the frontend E2E opt-in GitHub Actions workflow.

These tests were previously failing because they still checked for the
literal strings `make frontend-e2e-mocked` and `make frontend-e2e-smoke`
after the workflow was updated to use direct npm/Playwright invocations.

Fix (Recommendation 2)
-----------------------
The assertions now match the *actual* workflow implementation:
  - `npx playwright test` from `app/frontend`
  - `PLAYWRIGHT_MOCK_API` env var for the mocked run

The old `make` command strings are no longer required in the workflow
YAML (they may still exist as Makefile convenience shims, but the
workflow itself should not depend on them).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "frontend-e2e.yml"


@pytest.fixture(scope="module")
def workflow_content() -> str:
    if not WORKFLOW_PATH.exists():
        pytest.skip(f"Workflow file not found: {WORKFLOW_PATH}")
    return WORKFLOW_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# New-contract assertions (npm / Playwright direct invocation)
# ---------------------------------------------------------------------------

class TestFrontendE2EWorkflowNewContract:
    """Assert the workflow uses the current npm/Playwright invocation form."""

    def test_workflow_file_exists(self) -> None:
        assert WORKFLOW_PATH.exists(), (
            f"Expected frontend E2E workflow at {WORKFLOW_PATH}"
        )

    def test_working_directory_is_app_frontend(self, workflow_content: str) -> None:
        assert re.search(
            r"working-directory\s*:\s*app/frontend", workflow_content, re.MULTILINE
        ), (
            "Workflow must declare `working-directory: app/frontend` so that "
            "npx and npm commands resolve correctly."
        )

    def test_playwright_invoked_via_npx(self, workflow_content: str) -> None:
        assert "npx playwright test" in workflow_content, (
            "Workflow must invoke Playwright via `npx playwright test` "
            "(not via a Makefile wrapper)."
        )

    def test_mock_api_env_var_present(self, workflow_content: str) -> None:
        assert re.search(
            r"PLAYWRIGHT_MOCK_API\s*[:=]", workflow_content, re.MULTILINE
        ), (
            "Workflow must set PLAYWRIGHT_MOCK_API for the mocked E2E run step. "
            "Example: `PLAYWRIGHT_MOCK_API: '1'`"
        )

    def test_workflow_has_on_workflow_dispatch_or_push(
        self, workflow_content: str
    ) -> None:
        """Workflow must be triggerable (on: push, pull_request, or workflow_dispatch)."""
        assert re.search(
            r"^on\s*:", workflow_content, re.MULTILINE
        ), "Workflow must have an `on:` trigger block."

    def test_workflow_has_explicit_opt_in_comment_or_condition(
        self, workflow_content: str
    ) -> None:
        """Opt-in nature should be documented or enforced via a condition/label."""
        has_condition = (
            "if:" in workflow_content
            or "workflow_dispatch" in workflow_content
            or "# opt-in" in workflow_content.lower()
        )
        assert has_condition, (
            "Opt-in E2E workflow should gate execution via `if:` condition, "
            "`workflow_dispatch` trigger, or an explicit opt-in comment."
        )


# ---------------------------------------------------------------------------
# Negative assertions – old contract must NOT be the execution mechanism
# ---------------------------------------------------------------------------

class TestFrontendE2EWorkflowNoLegacyMakeCommands:
    """The workflow run steps must not call make for E2E execution.

    Note: make shim targets may still exist in the Makefile for local
    developer convenience – these tests only concern the *workflow* YAML.
    """

    def test_workflow_run_steps_do_not_call_make_frontend_e2e_mocked(
        self, workflow_content: str
    ) -> None:
        # A `run:` step containing `make frontend-e2e-mocked` is the old contract.
        match = re.search(
            r"^\s*run\s*:.*make frontend-e2e-mocked",
            workflow_content,
            re.MULTILINE,
        )
        assert not match, (
            "Workflow `run:` step must not call `make frontend-e2e-mocked`. "
            "Inline the npx playwright command instead:\n"
            "  cd app/frontend && PLAYWRIGHT_MOCK_API=1 npx playwright test "
            "tests/e2e/learner-mocked-api-journey.spec.ts"
        )

    def test_workflow_run_steps_do_not_call_make_frontend_e2e_smoke(
        self, workflow_content: str
    ) -> None:
        match = re.search(
            r"^\s*run\s*:.*make frontend-e2e-smoke",
            workflow_content,
            re.MULTILINE,
        )
        assert not match, (
            "Workflow `run:` step must not call `make frontend-e2e-smoke`. "
            "Inline the npx playwright command instead:\n"
            "  cd app/frontend && npx playwright test "
            "tests/e2e/learner-vertical-journey.spec.ts "
            "tests/e2e/parent-vertical-journey.spec.ts"
        )
