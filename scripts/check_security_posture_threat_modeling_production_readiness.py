#!/usr/bin/env python3
"""Validate production-readiness item 15: security posture and threat modeling."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.security_posture.production_readiness_contracts import default_security_posture_readiness_report


REQUIRED_FILES = (
    "app/modules/security_posture/__init__.py",
    "app/modules/security_posture/production_readiness_contracts.py",
    "docs/adr/ADR-015-security-posture-threat-modeling.md",
    "docs/security/security_posture_architecture_contract.md",
    "docs/security/threat_model_register.md",
    "docs/security/security_control_register.md",
    "docs/security/vulnerability_management_policy.md",
    "docs/security/security_test_strategy_contract.md",
    "docs/security/secret_hygiene_contract.md",
    "docs/security/supply_chain_security_contract.md",
    "docs/security/security_headers_policy.md",
    "docs/security/pii_secret_redaction_contract.md",
    "docs/security/risk_acceptance_register.md",
    "docs/security/runbooks/security_incident_response.md",
    "docs/backlog/production_readiness/15_security_posture_and_threat_modeling.md",
    "tests/unit/test_security_posture_threat_modeling_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/security_posture/production_readiness_contracts.py": (
        "class SecurityDomain",
        "class ThreatCategory",
        "class ControlStatus",
        "class VulnerabilitySeverity",
        "class SecurityTestType",
        "class IncidentSeverity",
        "SecurityPostureDecision",
        "ThreatModelEntry",
        "SecurityControl",
        "VulnerabilityPolicy",
        "SecurityTestContract",
        "SecretHygieneRule",
        "SupplyChainControl",
        "SecurityIncidentRunbook",
        "RiskAcceptanceRecord",
        "contains_secret_value",
        "redact_secret_values",
        "compute_security_evidence_checksum",
        "validate_security_headers",
        "default_security_posture_readiness_report",
    ),
    "docs/adr/ADR-015-security-posture-threat-modeling.md": (
        "Security Posture and Threat Modeling Decision",
        "threat model is required",
        "secure defaults are required",
        "vulnerability management is required",
        "secret scanning is required",
        "supply-chain controls are required",
        "critical risks cannot be accepted for production by default",
    ),
    "docs/security/security_posture_architecture_contract.md": (
        "Security Posture Architecture Contract",
        "authentication",
        "authorization",
        "AI safety",
        "supply-chain security",
        "threat model register",
        "risk acceptance register",
        "release-blocking security gate",
    ),
    "docs/security/threat_model_register.md": (
        "Threat Model Register",
        "spoofing",
        "tampering",
        "information disclosure",
        "prompt injection",
        "supply-chain compromise",
        "abuse case",
        "residual risk",
    ),
    "docs/security/security_control_register.md": (
        "Security Control Register",
        "control ID",
        "implementation status",
        "production blocking flag",
        "secure session defaults",
        "object-level authorization",
        "vulnerability scan gate",
    ),
    "docs/security/vulnerability_management_policy.md": (
        "Vulnerability Management Policy",
        "high vulnerabilities must block release",
        "critical vulnerabilities must block release",
        "every vulnerability requires CVE or finding ID",
        "critical vulnerabilities require remediation within 3 days",
    ),
    "docs/security/security_test_strategy_contract.md": (
        "Security Test Strategy Contract",
        "SAST",
        "dependency scan",
        "secret scan",
        "container scan",
        "API fuzzing",
        "production security tests must block release",
    ),
    "docs/security/secret_hygiene_contract.md": (
        "Secret Hygiene Contract",
        "API keys and tokens are detected",
        "private keys are detected",
        "secret exposure blocks commit or merge",
        "exposed secrets require rotation",
        "raw secret values must not be logged",
    ),
    "docs/security/supply_chain_security_contract.md": (
        "Supply Chain Security Contract",
        "dependency lockfile is required",
        "SBOM is required",
        "artifact provenance is required",
        "dependency review is required",
        "signed artifact or digest pinning is required",
    ),
    "docs/security/security_headers_policy.md": (
        "Security Headers Policy",
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
    ),
    "docs/security/risk_acceptance_register.md": (
        "Risk Acceptance Register",
        "critical risks cannot be accepted for production by default",
        "accepted risks must expire",
        "accepted risks require compensating controls",
    ),
    "docs/backlog/production_readiness/15_security_posture_and_threat_modeling.md": (
        "15.6 Repository-side implementation evidence",
        "docs/security/security_posture_architecture_contract.md",
        "scripts/check_security_posture_threat_modeling_production_readiness.py",
        "make security-posture-threat-modeling-production-readiness-check",
    ),
    "Makefile": (
        "security-posture-threat-modeling-production-readiness-check:",
        "scripts/check_security_posture_threat_modeling_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class SecurityPostureReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[SecurityPostureReadinessResult]:
    results: list[SecurityPostureReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            SecurityPostureReadinessResult(
                rel_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                SecurityPostureReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_security_posture_readiness_report()
        results.extend(
            [
                SecurityPostureReadinessResult("security_posture_contracts", report["decision_issues"] == [], "security posture decision validates"),
                SecurityPostureReadinessResult("security_posture_contracts", report["threat_model_issues"] == [], "threat model validates"),
                SecurityPostureReadinessResult("security_posture_contracts", report["security_control_issues"] == [], "security controls validate"),
                SecurityPostureReadinessResult("security_posture_contracts", report["vulnerability_policy_issues"] == [], "vulnerability policies validate"),
                SecurityPostureReadinessResult("security_posture_contracts", report["security_test_issues"] == [], "security tests validate"),
                SecurityPostureReadinessResult("security_posture_contracts", report["secret_rule_issues"] == [], "secret hygiene rules validate"),
                SecurityPostureReadinessResult("security_posture_contracts", report["supply_chain_issues"] == [], "supply-chain controls validate"),
                SecurityPostureReadinessResult("security_posture_contracts", report["incident_runbook_issues"] == [], "incident runbooks validate"),
                SecurityPostureReadinessResult("security_posture_contracts", report["risk_acceptance_issues"] == [], "risk acceptance records validate"),
                SecurityPostureReadinessResult("security_posture_contracts", report["security_header_issues"] == [], "security header sample validates"),
                SecurityPostureReadinessResult("security_posture_contracts", report["secret_detection_sample"] is True, "secret detection sample passes"),
                SecurityPostureReadinessResult("security_posture_contracts", "[redacted-secret]" in str(report["secret_redaction_sample"]), "secret redaction sample passes"),
                SecurityPostureReadinessResult("security_posture_contracts", len(str(report["checksum_sample"])) == 64, "security checksum sample passes"),
            ]
        )
    except Exception as exc:  # pragma: no cover - defensive CLI output
        results.append(SecurityPostureReadinessResult("security_posture_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Security posture threat modeling production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
