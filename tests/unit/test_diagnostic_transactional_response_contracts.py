from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.diagnostic_transactional_response import (
    DiagnosticTransactionError,
    DiagnosticTransactionInput,
    DiagnosticTransactionResult,
    TransactionalDiagnosticResponseService,
)


ROOT = Path(__file__).resolve().parents[2]


def test_diagnostic_transactional_response_exports_expected_symbols():
    assert DiagnosticTransactionInput
    assert DiagnosticTransactionResult
    assert DiagnosticTransactionError
    assert TransactionalDiagnosticResponseService


def test_diagnostic_transactional_response_uses_explicit_transaction_boundary():
    source = (ROOT / "app/services/diagnostic_transactional_response.py").read_text(encoding="utf-8")

    assert "async with self.session.begin()" in source
    assert "fail_after_response" in source
    assert "fail_after_mastery" in source
    assert "fail_after_audit" in source
    assert "diagnostic.response_submitted" in source


def test_diagnostic_transaction_rollback_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_diagnostics_transaction_rollback_proof.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_diagnostic_transaction_rollback_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "diagnostics-transaction-rollback-proof-test:" in source
    assert "diagnostics-transaction-rollback-proof-check:" in source
    assert "backend-implementation-1511-1550-full-check:" in source
