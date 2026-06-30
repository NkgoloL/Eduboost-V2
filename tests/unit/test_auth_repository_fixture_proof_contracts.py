from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_auth_repository_candidate_order_prefers_session_bound_canonical_repositories():
    source = (ROOT / "app/services/auth_application_service.py").read_text(encoding="utf-8")

    assert source.index("app.repositories.repositories.LearnerRepository") < source.index("app.repositories.learner_repository.LearnerRepository")
    assert source.index("app.repositories.repositories.ConsentRepository") < source.index("app.repositories.consent_repository.ConsentRepository")


def test_auth_runtime_boundary_candidate_order_prefers_session_bound_canonical_repositories():
    source = (ROOT / "app/services/auth_runtime_boundary.py").read_text(encoding="utf-8")

    assert source.index("app.repositories.repositories.LearnerRepository") < source.index("app.repositories.learner_repository.LearnerRepository")
    assert source.index("app.repositories.repositories.ConsentRepository") < source.index("app.repositories.consent_repository.ConsentRepository")


def test_auth_repository_fixture_checker_runs():
    import os
    if os.environ.get("IN_SUBPROCESS_CHECK"):
        return
    env = os.environ.copy()
    env["IN_SUBPROCESS_CHECK"] = "1"
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_repository_fixture_proof.py"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_auth_repository_fixture_report_exists():
    assert (ROOT / "docs/release/auth_repository_fixture_proof_report.md").exists()
    assert (ROOT / "docs/release/auth_repository_fixture_proof_report.json").exists()


def test_makefile_contains_auth_repository_fixture_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-repository-fixture-proof-test:" in text
    assert "backend-implementation-1271-1310-full-check:" in text
