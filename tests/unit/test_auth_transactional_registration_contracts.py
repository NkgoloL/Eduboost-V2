from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.auth_transactional_registration import (
    AuthRegistrationInput,
    AuthRegistrationResult,
    AuthRegistrationTransactionError,
    TransactionalAuthRegistrationService,
)


ROOT = Path(__file__).resolve().parents[2]


def test_auth_transactional_registration_exports_expected_symbols():
    assert AuthRegistrationInput
    assert AuthRegistrationResult
    assert AuthRegistrationTransactionError
    assert TransactionalAuthRegistrationService


def test_auth_transactional_registration_uses_explicit_transaction_boundary():
    source = (ROOT / "app/services/auth_transactional_registration.py").read_text(encoding="utf-8")

    assert "async with self.session.begin()" in source
    assert "fail_after_user" in source
    assert "fail_after_guardian" in source
    assert "fail_after_learner" in source


def test_auth_transaction_rollback_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_auth_transaction_rollback_proof.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_auth_transaction_rollback_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "auth-transaction-rollback-proof-test:" in source
    assert "auth-transaction-rollback-proof-check:" in source
    assert "backend-implementation-1471-1510-full-check:" in source
