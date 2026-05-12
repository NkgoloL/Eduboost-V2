"""
scripts/check_frontend_e2e_opt_in_workflow.py
=============================================
Verify that the frontend E2E opt-in GitHub Actions workflow uses the
current npm/Playwright invocation contract (running from app/frontend)
rather than the legacy `make frontend-e2e-mocked` / `make frontend-e2e-smoke`
commands.

Background (Recommendation 2)
------------------------------
After the workflow was updated to run Playwright directly from app/frontend,
the evidence checker still asserted the old `make` command strings.  This
produced false failures in:
  - tests/unit/test_frontend_e2e_opt_in_workflow.py
  - tests/unit/test_cluster_g_*.py

This script is the authoritative runtime source for those contract checks.
It is also invoked by:
  make frontend-e2e-opt-in-workflow-check

Contract being asserted
-----------------------
The workflow file must contain:
  1. A working-directory declaration pointing to app/frontend.
  2. A `npx playwright test` invocation (the new contract).
  3. A PLAYWRIGHT_MOCK_API env var reference for the mocked run.

It must NOT require:
  - `make frontend-e2e-mocked`
  - `make frontend-e2e-smoke`
  (those strings may still appear in Makefile shim targets – that is fine –
   but the *workflow* should use the direct npm/Playwright form.)
"""

from __future__ import annotations

import sys
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_FILE = REPO_ROOT / ".github" / "workflows" / "frontend-e2e.yml"

# Patterns the workflow MUST match (new contract)
REQUIRED_PATTERNS: list[tuple[str, str]] = [
    (
        r"working-directory\s*:\s*app/frontend",
        "working-directory must be set to app/frontend",
    ),
    (
        r"npx playwright test",
        "Playwright must be invoked via `npx playwright test`",
    ),
    (
        r"PLAYWRIGHT_MOCK_API\s*[:=]",
        "PLAYWRIGHT_MOCK_API env var must be referenced for mocked runs",
    ),
]

# Patterns the workflow must NOT use as the execution mechanism
# (they may exist as Make targets, but the workflow should not call make for E2E)
FORBIDDEN_AS_RUN_STEPS: list[tuple[str, str]] = [
    (
        r"^\s*-?\s*run\s*:.*make frontend-e2e-mocked",
        "Workflow run step must not call `make frontend-e2e-mocked` directly; "
        "use `npx playwright test` from app/frontend instead.",
    ),
    (
        r"^\s*-?\s*run\s*:.*make frontend-e2e-smoke",
        "Workflow run step must not call `make frontend-e2e-smoke` directly; "
        "use `npx playwright test` from app/frontend instead.",
    ),
]


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------

def check_workflow(path: Path) -> list[str]:
    """Return a list of human-readable failure messages (empty = pass)."""
    if not path.exists():
        return [f"Workflow file not found: {path}"]

    content = path.read_text(encoding="utf-8")
    failures: list[str] = []

    for pattern, description in REQUIRED_PATTERNS:
        if not re.search(pattern, content, re.MULTILINE):
            failures.append(f"MISSING – {description}\n  Pattern: {pattern!r}")

    for pattern, description in FORBIDDEN_AS_RUN_STEPS:
        if re.search(pattern, content, re.MULTILINE):
            failures.append(f"FORBIDDEN – {description}\n  Pattern: {pattern!r}")

    return failures


def main() -> int:
    print(f"Checking E2E workflow contract: {WORKFLOW_FILE}")
    failures = check_workflow(WORKFLOW_FILE)

    if failures:
        print("\n[FAIL] Frontend E2E opt-in workflow contract violations:\n")
        for msg in failures:
            print(f"  • {msg}")
        print(
            "\nTo fix: update the workflow to use `npx playwright test` from "
            "app/frontend instead of `make frontend-e2e-*` commands.\n"
            "See Makefile targets `frontend-e2e-smoke` and `frontend-e2e-mocked` "
            "for the exact commands to inline."
        )
        return 1

    print("[PASS] Frontend E2E opt-in workflow contract is satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
