from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.backend_runtime_wiring_cases import (
    all_wiring_cases_pass,
    run_audit_wiring_cases,
    run_consent_wiring_cases,
    run_deep_readiness_wiring_cases,
)


ROOT = Path(__file__).resolve().parents[2]


def test_audit_runtime_wiring_cases_pass():
    results = run_audit_wiring_cases()
    assert results
    assert all(result.passed for result in results)


def test_consent_runtime_wiring_cases_pass():
    results = run_consent_wiring_cases()
    assert results
    assert all(result.passed for result in results)


def test_deep_readiness_wiring_cases_pass():
    results = run_deep_readiness_wiring_cases()
    assert results
    assert all(result.passed for result in results)


def test_all_wiring_cases_pass():
    assert all_wiring_cases_pass() is True


def test_runtime_wiring_case_check_and_report_run():
    for command in [
        [sys.executable, "scripts/check_backend_runtime_wiring_cases.py"],
        [sys.executable, "scripts/generate_backend_runtime_wiring_cases_report.py"],
    ]:
        result = subprocess.run(
            command,
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert result.returncode == 0, result.stdout


def test_makefile_contains_383_390_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-runtime-wiring-cases-check:" in text
    assert "backend-runtime-wiring-cases-report:" in text
    assert "backend-implementation-383-390-full-check:" in text
