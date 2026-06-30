from __future__ import annotations

import subprocess
import sys

import pytest

from scripts.check_learner_authz_coverage import ALLOWLIST, main


@pytest.mark.unit
def test_learner_authz_coverage_check_passes_current_routes() -> None:
    assert main() == 0


@pytest.mark.unit
def test_learner_authz_coverage_allowlist_documents_boundary_routes() -> None:
    assert ("auth.py", "POST", "/dev-session") in ALLOWLIST
    assert ("gamification.py", "GET", "/leaderboard") in ALLOWLIST


@pytest.mark.unit
def test_learner_authz_coverage_script_runs_directly() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_learner_authz_coverage.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Learner authorization coverage check" in result.stdout
    assert "ALLOW auth.py POST /dev-session" in result.stdout


@pytest.mark.unit
def test_consent_renewal_is_covered_by_admin_marker_not_allowlist() -> None:
    from scripts.generate_learner_authz_matrix import collect_rows

    rows = collect_rows()
    matches = [
        row
        for row in rows
        if row.router == "consent_renewal.py"
        and row.method == "POST"
        and row.path == "/trigger-renewal-reminders"
    ]

    assert matches
    assert matches[0].status == "covered"
    assert matches[0].authz_marker == "require_admin"
    assert ("consent_renewal.py", "POST", "/trigger-renewal-reminders") not in ALLOWLIST


@pytest.mark.unit
def test_onboarding_questions_catalog_boundary_is_allowlisted_and_authenticated() -> None:
    from scripts.generate_learner_authz_matrix import collect_rows

    rows = collect_rows()
    matches = [
        row
        for row in rows
        if row.router == "onboarding.py"
        and row.method == "GET"
        and row.path == "/questions"
    ]

    assert matches
    assert matches[0].status == "covered"
    assert matches[0].authz_marker == "require_auth_context"
    assert ("onboarding.py", "GET", "/questions") in ALLOWLIST
