from __future__ import annotations

import subprocess
import sys

import pytest

from scripts.check_audit_event_contracts import run_checks


@pytest.mark.unit
def test_audit_event_contracts_have_required_markers() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_audit_event_contract_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_audit_event_contracts.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Audit event contract check" in result.stdout
