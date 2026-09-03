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


@pytest.mark.unit
def test_security_posture_contracts_validation_error_branches() -> None:
    from app.modules.security_posture.production_readiness_contracts import (
        ControlStatus,
        IncidentSeverity,
        RiskAcceptanceRecord,
        SecretHygieneRule,
        SecurityControl,
        SecurityDomain,
        SecurityIncidentRunbook,
        SecurityPostureDecision,
        SecurityTestContract,
        SecurityTestType,
        SupplyChainControl,
        ThreatCategory,
        ThreatModelEntry,
        VulnerabilityPolicy,
        VulnerabilitySeverity,
        default_security_posture_readiness_report,
    )

    # 1. SecurityPostureDecision invalid branches
    bad_dec = SecurityPostureDecision(
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        threat_model_required=False,
        secure_defaults_required=False,
        vulnerability_management_required=False,
        secret_scanning_required=False,
        dependency_scanning_required=False,
        incident_response_required=False,
        risk_acceptance_required=False,
    )
    assert len(bad_dec.validate()) == 9

    # 2. ThreatModelEntry invalid branches
    bad_threat = ThreatModelEntry(
        threat_id="",
        domain=SecurityDomain.AUTHENTICATION,
        category=ThreatCategory.SPOOFING,
        asset="",
        abuse_case="",
        control_summary="",
        residual_risk=VulnerabilitySeverity.CRITICAL,
        owner="",
        review_required=False,
    )
    threat_issues = bad_threat.validate()
    assert "threat_id is required" in threat_issues
    assert "asset is required" in threat_issues
    assert "abuse case is required" in threat_issues
    assert "control summary is required" in threat_issues
    assert "high or critical residual threat risk must be remediated or formally accepted" in threat_issues
    assert "threat owner is required" in threat_issues
    assert "threat model review is required" in threat_issues

    # 3. SecurityControl invalid branches
    bad_control = SecurityControl(
        control_id="",
        domain=SecurityDomain.AUTHENTICATION,
        name="",
        description="",
        status=ControlStatus.REQUIRED,
        evidence_path="invalid/path.md",
        owner="",
        production_blocking=True,
    )
    control_issues = bad_control.validate()
    assert "control_id is required" in control_issues
    assert "control name is required" in control_issues
    assert "control description is required" in control_issues
    assert "security evidence path must be controlled" in control_issues
    assert "security control owner is required" in control_issues
    assert any("production-blocking control must be implemented or verified" in issue for issue in control_issues)

    # 4. VulnerabilityPolicy invalid branches
    bad_vuln = VulnerabilityPolicy(
        severity=VulnerabilitySeverity.HIGH,
        max_age_days=0,
        blocks_release=False,
        requires_owner=False,
        requires_fix_or_accepted_risk=False,
        requires_cve_or_finding_id=False,
    )
    vuln_issues = bad_vuln.validate()
    assert "vulnerability max age must be positive" in vuln_issues
    assert "high vulnerabilities must block release" in vuln_issues
    assert "high vulnerabilities require owner" in vuln_issues
    assert "high vulnerabilities require fix or accepted risk" in vuln_issues
    assert "high vulnerabilities require CVE or finding ID" in vuln_issues

    # 5. SecurityTestContract invalid branches
    bad_test = SecurityTestContract(
        test_type=SecurityTestType.SAST,
        command="",
        required_for_pr=False,
        required_for_staging=True,
        required_for_production=True,
        artifact_path="invalid/path.json",
        owner="",
        blocks_release=False,
    )
    test_issues = bad_test.validate()
    assert "sast command is required" in test_issues
    assert "sast must run for PRs" in test_issues
    assert "sast artifact path must be controlled" in test_issues
    assert "sast owner is required" in test_issues
    assert "sast production security test must block release" in test_issues

    bad_prod_test = SecurityTestContract(
        test_type=SecurityTestType.DAST,
        command="make dast",
        required_for_pr=False,
        required_for_staging=False,
        required_for_production=True,
        artifact_path="artifacts/security/dast.json",
        owner="sec",
        blocks_release=True,
    )
    assert "dast production security test must also gate staging" in bad_prod_test.validate()

    # 6. SecretHygieneRule invalid branches
    bad_rule = SecretHygieneRule(
        rule_id="",
        description="",
        pattern_name="",
        applies_to_paths=(),
        blocks_commit=False,
        rotation_required_on_exposure=False,
        evidence_path="invalid/path.md",
    )
    assert len(bad_rule.validate()) == 7

    # 7. SupplyChainControl invalid branches
    bad_sc = SupplyChainControl(
        control_id="",
        lockfile_required=False,
        sbom_required=False,
        provenance_required=False,
        dependency_review_required=False,
        allowed_license_review_required=False,
        signed_artifact_required=False,
        owner="",
    )
    assert len(bad_sc.validate()) == 8

    # 8. SecurityIncidentRunbook invalid branches
    bad_runbook = SecurityIncidentRunbook(
        runbook_path="invalid/path.md",
        severity=IncidentSeverity.SEV1,
        triage_owner="",
        containment_steps=(),
        eradication_steps=(),
        recovery_steps=(),
        notification_steps=(),
        post_incident_review_required=False,
    )
    assert len(bad_runbook.validate()) == 7

    # 9. RiskAcceptanceRecord invalid branches
    bad_risk = RiskAcceptanceRecord(
        risk_id="",
        severity=VulnerabilitySeverity.CRITICAL,
        reason="",
        owner="",
        approver="",
        expires_days=100,
        compensating_controls=(),
        evidence_path="invalid/path.md",
    )
    risk_issues = bad_risk.validate()
    assert "risk_id is required" in risk_issues
    assert "critical risks cannot be accepted for production by default" in risk_issues
    assert "risk acceptance reason is required" in risk_issues
    assert "risk owner is required" in risk_issues
    assert "risk approver is required" in risk_issues
    assert "risk acceptance expiry must be between 1 and 90 days" in risk_issues
    assert "risk acceptance requires compensating controls" in risk_issues
    assert "risk acceptance evidence must live under docs/security/" in risk_issues

    # 10. default_security_posture_readiness_report
    report = default_security_posture_readiness_report()
    assert report["decision_issues"] == []
    assert report["secret_detection_sample"] is True
    assert "[redacted-secret]" in str(report["secret_redaction_sample"])
