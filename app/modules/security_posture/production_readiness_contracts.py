"""Repository-verifiable security posture and threat-modeling contracts.

These contracts do not run scanners, query cloud security posture APIs, or modify
infrastructure. They model deterministic requirements for threat models, secure
configuration, vulnerability management, dependency/SBOM controls, secrets hygiene,
security testing, incident response, and risk acceptance.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import re
from typing import Mapping


class SecurityDomain(StrEnum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    API = "api"
    DATA_PROTECTION = "data_protection"
    AI_SAFETY = "ai_safety"
    FRONTEND = "frontend"
    INFRASTRUCTURE = "infrastructure"
    SUPPLY_CHAIN = "supply_chain"
    OPERATIONS = "operations"
    PRIVACY = "privacy"


class ThreatCategory(StrEnum):
    SPOOFING = "spoofing"
    TAMPERING = "tampering"
    REPUDIATION = "repudiation"
    INFORMATION_DISCLOSURE = "information_disclosure"
    DENIAL_OF_SERVICE = "denial_of_service"
    ELEVATION_OF_PRIVILEGE = "elevation_of_privilege"
    PROMPT_INJECTION = "prompt_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    SUPPLY_CHAIN_COMPROMISE = "supply_chain_compromise"


class ControlStatus(StrEnum):
    REQUIRED = "required"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    ACCEPTED_RISK = "accepted_risk"
    NOT_APPLICABLE = "not_applicable"


class VulnerabilitySeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityTestType(StrEnum):
    SAST = "sast"
    DEPENDENCY_SCAN = "dependency_scan"
    SECRET_SCAN = "secret_scan"
    CONTAINER_SCAN = "container_scan"
    DAST = "dast"
    API_FUZZ = "api_fuzz"
    CONFIG_AUDIT = "config_audit"
    THREAT_MODEL_REVIEW = "threat_model_review"


class IncidentSeverity(StrEnum):
    SEV4 = "sev4"
    SEV3 = "sev3"
    SEV2 = "sev2"
    SEV1 = "sev1"


SECRET_VALUE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9]{20,}"),
    re.compile(r"(?i)ghp_[a-z0-9]{20,}"),
    re.compile(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(password|secret|token|api[_-]?key)\s*=\s*['\"]?[^'\"\s]{8,}"),
)


@dataclass(frozen=True)
class SecurityPostureDecision:
    adr_path: str
    architecture_doc_path: str
    threat_model_required: bool
    secure_defaults_required: bool
    vulnerability_management_required: bool
    secret_scanning_required: bool
    dependency_scanning_required: bool
    incident_response_required: bool
    risk_acceptance_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("security posture decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/security/"):
            issues.append("security architecture must be documented in docs/security/")
        for name, value in {
            "threat_model_required": self.threat_model_required,
            "secure_defaults_required": self.secure_defaults_required,
            "vulnerability_management_required": self.vulnerability_management_required,
            "secret_scanning_required": self.secret_scanning_required,
            "dependency_scanning_required": self.dependency_scanning_required,
            "incident_response_required": self.incident_response_required,
            "risk_acceptance_required": self.risk_acceptance_required,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        return issues


@dataclass(frozen=True)
class ThreatModelEntry:
    threat_id: str
    domain: SecurityDomain
    category: ThreatCategory
    asset: str
    abuse_case: str
    control_summary: str
    residual_risk: VulnerabilitySeverity
    owner: str
    review_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.threat_id:
            issues.append("threat_id is required")
        if not self.asset:
            issues.append("asset is required")
        if not self.abuse_case:
            issues.append("abuse case is required")
        if not self.control_summary:
            issues.append("control summary is required")
        if self.residual_risk in {VulnerabilitySeverity.HIGH, VulnerabilitySeverity.CRITICAL}:
            issues.append("high or critical residual threat risk must be remediated or formally accepted")
        if not self.owner:
            issues.append("threat owner is required")
        if not self.review_required:
            issues.append("threat model review is required")
        return issues


@dataclass(frozen=True)
class SecurityControl:
    control_id: str
    domain: SecurityDomain
    name: str
    description: str
    status: ControlStatus
    evidence_path: str
    owner: str
    production_blocking: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.control_id:
            issues.append("control_id is required")
        if not self.name:
            issues.append("control name is required")
        if not self.description:
            issues.append("control description is required")
        if self.status == ControlStatus.REQUIRED:
            issues.append(f"{self.control_id} is required but not implemented")
        if not self.evidence_path.startswith(("docs/", "scripts/", "tests/", ".github/")):
            issues.append("security evidence path must be controlled")
        if not self.owner:
            issues.append("security control owner is required")
        if self.production_blocking and self.status not in {ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED}:
            issues.append(f"{self.control_id} production-blocking control must be implemented or verified")
        return issues


@dataclass(frozen=True)
class VulnerabilityPolicy:
    severity: VulnerabilitySeverity
    max_age_days: int
    blocks_release: bool
    requires_owner: bool
    requires_fix_or_accepted_risk: bool
    requires_cve_or_finding_id: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.max_age_days <= 0:
            issues.append("vulnerability max age must be positive")
        if self.severity in {VulnerabilitySeverity.HIGH, VulnerabilitySeverity.CRITICAL} and not self.blocks_release:
            issues.append(f"{self.severity.value} vulnerabilities must block release")
        if not self.requires_owner:
            issues.append(f"{self.severity.value} vulnerabilities require owner")
        if not self.requires_fix_or_accepted_risk:
            issues.append(f"{self.severity.value} vulnerabilities require fix or accepted risk")
        if not self.requires_cve_or_finding_id:
            issues.append(f"{self.severity.value} vulnerabilities require CVE or finding ID")
        return issues


@dataclass(frozen=True)
class SecurityTestContract:
    test_type: SecurityTestType
    command: str
    required_for_pr: bool
    required_for_staging: bool
    required_for_production: bool
    artifact_path: str
    owner: str
    blocks_release: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.command:
            issues.append(f"{self.test_type.value} command is required")
        if self.required_for_production and not self.required_for_staging:
            issues.append(f"{self.test_type.value} production security test must also gate staging")
        if self.required_for_staging and not self.required_for_pr and self.test_type in {
            SecurityTestType.SAST,
            SecurityTestType.DEPENDENCY_SCAN,
            SecurityTestType.SECRET_SCAN,
        }:
            issues.append(f"{self.test_type.value} must run for PRs")
        if not self.artifact_path.startswith(("artifacts/security/", "docs/security/", "test-results/security/")):
            issues.append(f"{self.test_type.value} artifact path must be controlled")
        if not self.owner:
            issues.append(f"{self.test_type.value} owner is required")
        if self.required_for_production and not self.blocks_release:
            issues.append(f"{self.test_type.value} production security test must block release")
        return issues


@dataclass(frozen=True)
class SecretHygieneRule:
    rule_id: str
    description: str
    pattern_name: str
    applies_to_paths: tuple[str, ...]
    blocks_commit: bool
    rotation_required_on_exposure: bool
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.rule_id:
            issues.append("secret hygiene rule_id is required")
        if not self.description:
            issues.append("secret hygiene description is required")
        if not self.pattern_name:
            issues.append("secret hygiene pattern name is required")
        if not self.applies_to_paths:
            issues.append("secret hygiene path scope is required")
        if not self.blocks_commit:
            issues.append("secret exposure must block commit or merge")
        if not self.rotation_required_on_exposure:
            issues.append("secret exposure requires rotation")
        if not self.evidence_path.startswith(("docs/security/", "scripts/", ".github/")):
            issues.append("secret hygiene evidence path must be controlled")
        return issues


@dataclass(frozen=True)
class SupplyChainControl:
    control_id: str
    lockfile_required: bool
    sbom_required: bool
    provenance_required: bool
    dependency_review_required: bool
    allowed_license_review_required: bool
    signed_artifact_required: bool
    owner: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.control_id:
            issues.append("supply-chain control_id is required")
        if not self.lockfile_required:
            issues.append("dependency lockfile is required")
        if not self.sbom_required:
            issues.append("SBOM is required")
        if not self.provenance_required:
            issues.append("artifact provenance is required")
        if not self.dependency_review_required:
            issues.append("dependency review is required")
        if not self.allowed_license_review_required:
            issues.append("license review is required")
        if not self.signed_artifact_required:
            issues.append("signed artifact or digest pinning is required")
        if not self.owner:
            issues.append("supply-chain owner is required")
        return issues


@dataclass(frozen=True)
class SecurityIncidentRunbook:
    runbook_path: str
    severity: IncidentSeverity
    triage_owner: str
    containment_steps: tuple[str, ...]
    eradication_steps: tuple[str, ...]
    recovery_steps: tuple[str, ...]
    notification_steps: tuple[str, ...]
    post_incident_review_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.runbook_path.startswith("docs/security/runbooks/"):
            issues.append("security incident runbook must live under docs/security/runbooks/")
        if not self.triage_owner:
            issues.append("security incident triage owner is required")
        if not self.containment_steps:
            issues.append("containment steps are required")
        if not self.eradication_steps:
            issues.append("eradication steps are required")
        if not self.recovery_steps:
            issues.append("recovery steps are required")
        if not self.notification_steps:
            issues.append("notification steps are required")
        if not self.post_incident_review_required:
            issues.append("post-incident review is required")
        return issues


@dataclass(frozen=True)
class RiskAcceptanceRecord:
    risk_id: str
    severity: VulnerabilitySeverity
    reason: str
    owner: str
    approver: str
    expires_days: int
    compensating_controls: tuple[str, ...]
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.risk_id:
            issues.append("risk_id is required")
        if self.severity == VulnerabilitySeverity.CRITICAL:
            issues.append("critical risks cannot be accepted for production by default")
        if not self.reason:
            issues.append("risk acceptance reason is required")
        if not self.owner:
            issues.append("risk owner is required")
        if not self.approver:
            issues.append("risk approver is required")
        if not (0 < self.expires_days <= 90):
            issues.append("risk acceptance expiry must be between 1 and 90 days")
        if not self.compensating_controls:
            issues.append("risk acceptance requires compensating controls")
        if not self.evidence_path.startswith("docs/security/"):
            issues.append("risk acceptance evidence must live under docs/security/")
        return issues


def contains_secret_value(text: str) -> bool:
    """Return whether text appears to contain a common secret pattern."""

    return any(pattern.search(text or "") for pattern in SECRET_VALUE_PATTERNS)


def redact_secret_values(text: str) -> str:
    """Redact common secret-like values from audit output."""

    redacted = text or ""
    for pattern in SECRET_VALUE_PATTERNS:
        redacted = pattern.sub("[redacted-secret]", redacted)
    return redacted


def compute_security_evidence_checksum(content: str) -> str:
    """Compute SHA-256 checksum for security evidence content."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_security_headers(headers: Mapping[str, str]) -> list[str]:
    """Validate minimum production web security headers."""

    required = {
        "strict-transport-security": "HSTS header is required",
        "content-security-policy": "Content-Security-Policy header is required",
        "x-content-type-options": "X-Content-Type-Options header is required",
        "x-frame-options": "X-Frame-Options header is required",
        "referrer-policy": "Referrer-Policy header is required",
    }
    lowered = {key.lower(): value for key, value in headers.items()}
    return [message for key, message in required.items() if not lowered.get(key)]


DEFAULT_SECURITY_DECISION = SecurityPostureDecision(
    adr_path="docs/adr/ADR-015-security-posture-threat-modeling.md",
    architecture_doc_path="docs/security/security_posture_architecture_contract.md",
    threat_model_required=True,
    secure_defaults_required=True,
    vulnerability_management_required=True,
    secret_scanning_required=True,
    dependency_scanning_required=True,
    incident_response_required=True,
    risk_acceptance_required=True,
)

DEFAULT_THREAT_MODEL = (
    ThreatModelEntry("TM-001", SecurityDomain.AUTHENTICATION, ThreatCategory.SPOOFING, "session token", "attacker reuses stolen session token", "short-lived tokens, secure cookies, audit logging", VulnerabilitySeverity.MEDIUM, "security-owner", True),
    ThreatModelEntry("TM-002", SecurityDomain.AUTHORIZATION, ThreatCategory.ELEVATION_OF_PRIVILEGE, "learner data", "parent accesses unrelated learner data", "object-level authorization and route-level tests", VulnerabilitySeverity.LOW, "engineering", True),
    ThreatModelEntry("TM-003", SecurityDomain.AI_SAFETY, ThreatCategory.PROMPT_INJECTION, "lesson generation", "prompt injection attempts to expose policy or PII", "prompt sanitization, output validation, refusal regression tests", VulnerabilitySeverity.MEDIUM, "ai-owner", True),
    ThreatModelEntry("TM-004", SecurityDomain.SUPPLY_CHAIN, ThreatCategory.SUPPLY_CHAIN_COMPROMISE, "dependencies", "malicious dependency enters build", "lockfiles, dependency review, SBOM, vulnerability scan", VulnerabilitySeverity.MEDIUM, "security-owner", True),
)

DEFAULT_SECURITY_CONTROLS = (
    SecurityControl("SEC-001", SecurityDomain.AUTHENTICATION, "Secure session defaults", "Secure cookie/session/token handling is required.", ControlStatus.VERIFIED, "docs/security/authentication_security_contract.md", "security-owner", True),
    SecurityControl("SEC-002", SecurityDomain.AUTHORIZATION, "Object-level authorization", "Route handlers must enforce tenant and object ownership.", ControlStatus.VERIFIED, "tests/unit/test_authorization_matrix_coverage.py", "engineering", True),
    SecurityControl("SEC-003", SecurityDomain.DATA_PROTECTION, "PII redaction", "Logs and telemetry must redact PII and secrets.", ControlStatus.VERIFIED, "docs/security/pii_secret_redaction_contract.md", "privacy", True),
    SecurityControl("SEC-004", SecurityDomain.SUPPLY_CHAIN, "SBOM and dependency review", "Dependencies require lockfiles, review, and SBOM evidence.", ControlStatus.IMPLEMENTED, "docs/security/supply_chain_security_contract.md", "security-owner", True),
)

DEFAULT_VULNERABILITY_POLICIES = (
    VulnerabilityPolicy(VulnerabilitySeverity.LOW, 90, False, True, True, True),
    VulnerabilityPolicy(VulnerabilitySeverity.MEDIUM, 30, False, True, True, True),
    VulnerabilityPolicy(VulnerabilitySeverity.HIGH, 14, True, True, True, True),
    VulnerabilityPolicy(VulnerabilitySeverity.CRITICAL, 3, True, True, True, True),
)

DEFAULT_SECURITY_TESTS = (
    SecurityTestContract(SecurityTestType.SAST, "make security-sast", True, True, True, "artifacts/security/sast.json", "security-owner", True),
    SecurityTestContract(SecurityTestType.DEPENDENCY_SCAN, "make dependency-scan", True, True, True, "artifacts/security/dependencies.json", "security-owner", True),
    SecurityTestContract(SecurityTestType.SECRET_SCAN, "make secret-scan", True, True, True, "artifacts/security/secrets.json", "security-owner", True),
    SecurityTestContract(SecurityTestType.CONTAINER_SCAN, "make container-scan", False, True, True, "artifacts/security/container.json", "security-owner", True),
    SecurityTestContract(SecurityTestType.CONFIG_AUDIT, "make security-config-audit", True, True, True, "artifacts/security/config-audit.json", "security-owner", True),
    SecurityTestContract(SecurityTestType.THREAT_MODEL_REVIEW, "make threat-model-review", True, True, True, "docs/security/threat_model_register.md", "security-owner", True),
)

DEFAULT_SECRET_RULES = (
    SecretHygieneRule("SH-001", "Detect API keys and tokens", "api_key_token", ("app/", "scripts/", "docs/", ".github/"), True, True, "docs/security/secret_hygiene_contract.md"),
    SecretHygieneRule("SH-002", "Detect private keys", "private_key", ("app/", "scripts/", "docs/", ".github/"), True, True, "docs/security/secret_hygiene_contract.md"),
)

DEFAULT_SUPPLY_CHAIN = SupplyChainControl(
    "SC-001",
    lockfile_required=True,
    sbom_required=True,
    provenance_required=True,
    dependency_review_required=True,
    allowed_license_review_required=True,
    signed_artifact_required=True,
    owner="security-owner",
)

DEFAULT_INCIDENT_RUNBOOKS = (
    SecurityIncidentRunbook(
        "docs/security/runbooks/security_incident_response.md",
        IncidentSeverity.SEV1,
        "security-owner",
        ("disable affected credential", "isolate affected service"),
        ("remove malicious change", "rotate exposed secrets"),
        ("restore trusted artifact", "verify smoke tests"),
        ("notify release owner", "notify privacy owner where applicable"),
        True,
    ),
)

DEFAULT_RISK_ACCEPTANCES = (
    RiskAcceptanceRecord(
        "RA-001",
        VulnerabilitySeverity.MEDIUM,
        "temporary non-critical dependency update window",
        "security-owner",
        "release-owner",
        30,
        ("monitoring", "dependency pinning", "follow-up patch task"),
        "docs/security/risk_acceptance_register.md",
    ),
)


def default_security_posture_readiness_report() -> dict[str, object]:
    """Return deterministic security posture readiness evidence."""

    good_headers = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    secret_sample = "API_TOKEN=sk-abcdefghijklmnopqrstuvwxyz"

    return {
        "decision_issues": DEFAULT_SECURITY_DECISION.validate(),
        "threat_model_issues": [issue for threat in DEFAULT_THREAT_MODEL for issue in threat.validate()],
        "security_control_issues": [issue for control in DEFAULT_SECURITY_CONTROLS for issue in control.validate()],
        "vulnerability_policy_issues": [issue for policy in DEFAULT_VULNERABILITY_POLICIES for issue in policy.validate()],
        "security_test_issues": [issue for test in DEFAULT_SECURITY_TESTS for issue in test.validate()],
        "secret_rule_issues": [issue for rule in DEFAULT_SECRET_RULES for issue in rule.validate()],
        "supply_chain_issues": DEFAULT_SUPPLY_CHAIN.validate(),
        "incident_runbook_issues": [issue for runbook in DEFAULT_INCIDENT_RUNBOOKS for issue in runbook.validate()],
        "risk_acceptance_issues": [issue for risk in DEFAULT_RISK_ACCEPTANCES for issue in risk.validate()],
        "security_header_issues": validate_security_headers(good_headers),
        "secret_detection_sample": contains_secret_value(secret_sample),
        "secret_redaction_sample": redact_secret_values(secret_sample),
        "checksum_sample": compute_security_evidence_checksum("security-evidence"),
    }
