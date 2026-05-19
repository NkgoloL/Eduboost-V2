from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_transactional_lifecycle_service_declares_atomic_boundary():
    source = (ROOT / "app/services/popia_transactional_lifecycle.py").read_text(encoding="utf-8")

    assert "TransactionalPOPIAConsentLifecycleService" in source
    assert "async with _transaction_context(self.db)" in source
    assert "consent_record = await _call_flexible" in source
    assert "await self._audit" in source


def test_transactional_lifecycle_service_supports_required_transitions():
    source = (ROOT / "app/services/popia_transactional_lifecycle.py").read_text(encoding="utf-8")

    for method in ["grant", "deny", "withdraw", "renew"]:
        assert f"async def {method}" in source


def test_popia_transaction_rollback_checker_runs_without_nested_pytest_recursion():
    env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
    result = subprocess.run(
        [sys.executable, "scripts/check_popia_transaction_rollback_proof.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_popia_transaction_rollback_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-transaction-rollback-proof-test:" in text
    assert "backend-implementation-1431-1470-full-check:" in text
