from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.operations_support.production_readiness_contracts import (
    DEFAULT_HANDOVER,
    DEFAULT_INCIDENT_CLASSIFICATION,
    DEFAULT_INCIDENT_RECORD,
    DEFAULT_ON_CALL_POLICIES,
    DEFAULT_OPERATIONS_DECISION,
    DEFAULT_POST_INCIDENT_REVIEW,
    DEFAULT_RUNBOOKS,
    DEFAULT_STATUS_TEMPLATES,
    DEFAULT_SUPPORT_SLAS,
    CustomerImpact,
    SupportPriority,
    classify_support_priority,
    compute_operations_evidence_checksum,
    redact_incident_note,
)
from scripts.check_incident_response_operations_support_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_incident_response_operations_support_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_incident_response_operations_support_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_incident_response_operations_support_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Incident response operations support production readiness check" in result.stdout


@pytest.mark.unit
def test_operations_support_contracts_validate() -> None:
    assert DEFAULT_OPERATIONS_DECISION.validate() == []
    assert [issue for rule in DEFAULT_INCIDENT_CLASSIFICATION for issue in rule.validate()] == []
    assert [issue for policy in DEFAULT_ON_CALL_POLICIES for issue in policy.validate()] == []
    assert [issue for runbook in DEFAULT_RUNBOOKS for issue in runbook.validate()] == []
    assert [issue for sla in DEFAULT_SUPPORT_SLAS for issue in sla.validate()] == []
    assert [issue for template in DEFAULT_STATUS_TEMPLATES for issue in template.validate()] == []
    assert DEFAULT_INCIDENT_RECORD.validate() == []
    assert DEFAULT_POST_INCIDENT_REVIEW.validate() == []
    assert DEFAULT_HANDOVER.validate() == []


@pytest.mark.unit
def test_support_priority_classification() -> None:
    assert classify_support_priority(CustomerImpact.CRITICAL, False) == SupportPriority.P0
    assert classify_support_priority(CustomerImpact.MINOR, True) == SupportPriority.P0
    assert classify_support_priority(CustomerImpact.MAJOR, False) == SupportPriority.P1
    assert classify_support_priority(CustomerImpact.MODERATE, False) == SupportPriority.P2
    assert classify_support_priority(CustomerImpact.MINOR, False) == SupportPriority.P3


@pytest.mark.unit
def test_incident_note_redaction() -> None:
    redacted = redact_incident_note("Contact user@example.com or +27 82 123 4567")
    assert "user@example.com" not in redacted
    assert "+27 82 123 4567" not in redacted
    assert "[redacted-email]" in redacted
    assert "[redacted-phone]" in redacted


@pytest.mark.unit
def test_operations_evidence_checksum_is_sha256_hex() -> None:
    checksum = compute_operations_evidence_checksum("operations-support-evidence")
    assert len(checksum) == 64
    assert checksum == compute_operations_evidence_checksum("operations-support-evidence")
    assert checksum != compute_operations_evidence_checksum("other-operations-evidence")


@pytest.mark.unit
def test_makefile_exposes_incident_response_operations_support_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "incident-response-operations-support-production-readiness-check:" in text
    assert "scripts/check_incident_response_operations_support_production_readiness.py" in text
