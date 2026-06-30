from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.security_posture.production_readiness_contracts import (
    DEFAULT_INCIDENT_RUNBOOKS,
    DEFAULT_RISK_ACCEPTANCES,
    DEFAULT_SECRET_RULES,
    DEFAULT_SECURITY_CONTROLS,
    DEFAULT_SECURITY_DECISION,
    DEFAULT_SECURITY_TESTS,
    DEFAULT_SUPPLY_CHAIN,
    DEFAULT_THREAT_MODEL,
    DEFAULT_VULNERABILITY_POLICIES,
    compute_security_evidence_checksum,
    contains_secret_value,
    redact_secret_values,
    validate_security_headers,
)
from scripts.check_security_posture_threat_modeling_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_security_posture_threat_modeling_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_security_posture_threat_modeling_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_security_posture_threat_modeling_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Security posture threat modeling production readiness check" in result.stdout


@pytest.mark.unit
def test_security_posture_contracts_validate() -> None:
    assert DEFAULT_SECURITY_DECISION.validate() == []
    assert [issue for threat in DEFAULT_THREAT_MODEL for issue in threat.validate()] == []
    assert [issue for control in DEFAULT_SECURITY_CONTROLS for issue in control.validate()] == []
    assert [issue for policy in DEFAULT_VULNERABILITY_POLICIES for issue in policy.validate()] == []
    assert [issue for test in DEFAULT_SECURITY_TESTS for issue in test.validate()] == []
    assert [issue for rule in DEFAULT_SECRET_RULES for issue in rule.validate()] == []
    assert DEFAULT_SUPPLY_CHAIN.validate() == []
    assert [issue for runbook in DEFAULT_INCIDENT_RUNBOOKS for issue in runbook.validate()] == []
    assert [issue for risk in DEFAULT_RISK_ACCEPTANCES for issue in risk.validate()] == []


@pytest.mark.unit
def test_secret_detection_and_redaction() -> None:
    sample = "API_TOKEN=sk-abcdefghijklmnopqrstuvwxyz"
    redacted = redact_secret_values(sample)

    assert contains_secret_value(sample)
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "[redacted-secret]" in redacted


@pytest.mark.unit
def test_security_header_validation() -> None:
    good_headers = {
        "Strict-Transport-Security": "max-age=31536000",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    assert validate_security_headers(good_headers) == []
    assert "Content-Security-Policy header is required" in validate_security_headers({"Strict-Transport-Security": "max-age=31536000"})


@pytest.mark.unit
def test_security_evidence_checksum_is_sha256_hex() -> None:
    checksum = compute_security_evidence_checksum("security-evidence")
    assert len(checksum) == 64
    assert checksum == compute_security_evidence_checksum("security-evidence")
    assert checksum != compute_security_evidence_checksum("other-security-evidence")


@pytest.mark.unit
def test_makefile_exposes_security_posture_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "security-posture-threat-modeling-production-readiness-check:" in text
    assert "scripts/check_security_posture_threat_modeling_production_readiness.py" in text
