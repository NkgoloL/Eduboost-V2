from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.services.auth_db_lifecycle_proof import SQLiteAuthLifecycleProofStore


ROOT = Path(__file__).resolve().parents[2]


def test_auth_db_lifecycle_store_contract_register_login_refresh():
    store = SQLiteAuthLifecycleProofStore()
    registered = store.register(email="contract@example.com", password="Password123!")
    logged_in = store.login(email="contract@example.com", password="Password123!")
    refreshed = store.refresh(refresh_token=logged_in.refresh_token)
    assert registered.guardian_learner_ids
    assert logged_in.guardian_learner_ids == registered.guardian_learner_ids
    assert refreshed.guardian_learner_ids == registered.guardian_learner_ids


def test_auth_db_lifecycle_proof_scripts_run():
    for command in [
        [sys.executable, "scripts/generate_auth_db_lifecycle_proof_report.py"],
        [sys.executable, "scripts/check_auth_db_lifecycle_proof.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        assert result.returncode == 0, result.stdout


def test_auth_db_lifecycle_proof_reports_exist():
    assert (ROOT / "docs/release/auth_db_lifecycle_proof_report.md").exists()
    assert (ROOT / "docs/release/auth_db_lifecycle_proof_report.json").exists()


def test_makefile_contains_auth_db_lifecycle_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-db-lifecycle-proof-report:" in text
    assert "auth-db-lifecycle-proof-check:" in text
    assert "backend-implementation-1031-1070-full-check:" in text
