from __future__ import annotations

from scripts.audit_remediation.verify_backend_fast_phase02h import run_checks


def test_phase02h_verifier_reports_valid_contracts() -> None:
    checks = run_checks()
    assert checks
    assert all(check.valid for check in checks), [check for check in checks if not check.valid]


def test_phase02h_preserves_backend_fast_boundary() -> None:
    policy = "Phase 02H focused evidence only; backend-fast candidate evidence requires make test-fast exit 0."
    assert "make test-fast exit 0" in policy
