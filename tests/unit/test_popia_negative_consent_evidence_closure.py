from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_popia_consent_audit_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_negative_consent_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_popia_ci_runs_source_and_denial_path_tests() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "popia-consent-audit.yml").read_text(encoding="utf-8")

    assert "make popia-consent-source-check" in workflow
    assert "tests/unit/test_consent_dependency_denial_paths.py" in workflow
    assert "tests/unit/test_active_consent_route_sources.py" in workflow
