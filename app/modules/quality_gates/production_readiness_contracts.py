"""Repository-verifiable testing, release evidence, and quality-gate contracts.

These contracts model production-readiness expectations without calling CI providers,
GitHub branch protection APIs, deployment systems, or external test services. They
define deterministic evidence for test strategy, coverage thresholds, release gates,
manual approvals, evidence bundles, regression suites, and defect triage.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import re
from typing import Mapping


class TestLayer(str, Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    CONTRACT = "contract"
    E2E = "e2e"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SMOKE = "smoke"
    REGRESSION = "regression"


class QualityGateStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WAIVED = "waived"
    BLOCKED = "blocked"


class ReleaseStage(str, Enum):
    PULL_REQUEST = "pull_request"
    STAGING = "staging"
    BETA = "beta"
    PRODUCTION = "production"


class DefectSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    RELEASE_BLOCKER = "release_blocker"


class EvidenceType(str, Enum):
    TEST_REPORT = "test_report"
    COVERAGE_REPORT = "coverage_report"
    SECURITY_SCAN = "security_scan"
    ACCESSIBILITY_REPORT = "accessibility_report"
    PERFORMANCE_REPORT = "performance_report"
    OPENAPI_ARTIFACT = "openapi_artifact"
    RELEASE_APPROVAL = "release_approval"
    SMOKE_TEST_REPORT = "smoke_test_report"
    KNOWN_ISSUES_REGISTER = "known_issues_register"


@dataclass(frozen=True)
class TestingStrategyDecision:
    adr_path: str
    architecture_doc_path: str
    pytest_required: bool
    frontend_test_required: bool
    contract_test_required: bool
    e2e_test_required: bool
    security_test_required: bool
    accessibility_test_required: bool
    performance_test_required: bool
    release_evidence_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("testing strategy decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/testing/"):
            issues.append("testing architecture must be documented in docs/testing/")
        for name, value in {
            "pytest_required": self.pytest_required,
            "frontend_test_required": self.frontend_test_required,
            "contract_test_required": self.contract_test_required,
            "e2e_test_required": self.e2e_test_required,
            "security_test_required": self.security_test_required,
            "accessibility_test_required": self.accessibility_test_required,
            "performance_test_required": self.performance_test_required,
            "release_evidence_required": self.release_evidence_required,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        return issues


@dataclass(frozen=True)
class TestSuiteContract:
    layer: TestLayer
    command: str
    owner: str
    required_for_pr: bool
    required_for_staging: bool
    required_for_production: bool
    deterministic: bool
    artifact_path: str | None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.command:
            issues.append(f"{self.layer.value} test command is required")
        if not self.owner:
            issues.append(f"{self.layer.value} test owner is required")
        if self.required_for_production and not self.required_for_staging:
            issues.append(f"{self.layer.value} production tests must also gate staging")
        if self.required_for_pr and not self.deterministic:
            issues.append(f"{self.layer.value} PR tests must be deterministic")
        if self.layer in {TestLayer.SECURITY, TestLayer.ACCESSIBILITY, TestLayer.PERFORMANCE, TestLayer.E2E} and not self.artifact_path:
            issues.append(f"{self.layer.value} tests require evidence artifact path")
        if self.artifact_path and not self.artifact_path.startswith(("artifacts/", "docs/", "test-results/")):
            issues.append(f"{self.layer.value} artifact path must be controlled")
        return issues


@dataclass(frozen=True)
class CoverageThreshold:
    layer: TestLayer
    minimum_line_coverage: float
    minimum_branch_coverage: float
    measured_path: str
    ratchet_required: bool
    waiver_allowed: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not (0 <= self.minimum_line_coverage <= 100):
            issues.append("minimum line coverage must be between 0 and 100")
        if not (0 <= self.minimum_branch_coverage <= 100):
            issues.append("minimum branch coverage must be between 0 and 100")
        if self.minimum_line_coverage < 70:
            issues.append("production line coverage threshold must be at least 70 percent")
        if not self.measured_path:
            issues.append("coverage measured path is required")
        if not self.ratchet_required:
            issues.append("coverage ratchet is required")
        if self.layer == TestLayer.UNIT and self.waiver_allowed:
            issues.append("unit coverage waiver is not allowed by default")
        return issues


@dataclass(frozen=True)
class QualityGate:
    name: str
    release_stage: ReleaseStage
    required_layers: tuple[TestLayer, ...]
    required_evidence: tuple[EvidenceType, ...]
    manual_approval_required: bool
    waiver_policy_path: str
    blocks_release: bool
    owner: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.name:
            issues.append("quality gate name is required")
        if not self.required_layers:
            issues.append("quality gate requires at least one test layer")
        if not self.required_evidence:
            issues.append("quality gate requires evidence")
        if self.release_stage == ReleaseStage.PRODUCTION and not self.manual_approval_required:
            issues.append("production quality gate requires manual approval")
        if not self.waiver_policy_path.startswith("docs/testing/"):
            issues.append("quality gate waiver policy must live under docs/testing/")
        if self.release_stage in {ReleaseStage.BETA, ReleaseStage.PRODUCTION} and not self.blocks_release:
            issues.append("beta and production quality gates must block release")
        if not self.owner:
            issues.append("quality gate owner is required")
        return issues


@dataclass(frozen=True)
class ReleaseEvidenceItem:
    evidence_id: str
    evidence_type: EvidenceType
    path: str
    generated_by: str
    git_sha: str
    checksum_sha256: str
    required_for_stage: ReleaseStage
    retained: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.evidence_id:
            issues.append("evidence_id is required")
        if not self.path.startswith(("docs/", "artifacts/", "test-results/", "coverage.xml")):
            issues.append("evidence path must be controlled")
        if not self.generated_by:
            issues.append("generated_by is required")
        if not re.fullmatch(r"[a-f0-9]{7,40}", self.git_sha):
            issues.append("git_sha must be lowercase hex")
        if not re.fullmatch(r"[a-f0-9]{64}", self.checksum_sha256):
            issues.append("checksum_sha256 must be 64 lowercase hex characters")
        if self.required_for_stage in {ReleaseStage.BETA, ReleaseStage.PRODUCTION} and not self.retained:
            issues.append("beta and production evidence must be retained")
        return issues


@dataclass(frozen=True)
class DefectTriageRule:
    severity: DefectSeverity
    blocks_release: bool
    requires_owner: bool
    requires_fix_or_waiver: bool
    max_open_allowed_for_production: int
    sla_hours: int

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.severity in {DefectSeverity.CRITICAL, DefectSeverity.RELEASE_BLOCKER} and not self.blocks_release:
            issues.append(f"{self.severity.value} defects must block release")
        if not self.requires_owner:
            issues.append(f"{self.severity.value} defects require owner")
        if not self.requires_fix_or_waiver:
            issues.append(f"{self.severity.value} defects require fix or waiver")
        if self.severity == DefectSeverity.RELEASE_BLOCKER and self.max_open_allowed_for_production != 0:
            issues.append("release blockers allowed for production must be zero")
        if self.sla_hours <= 0:
            issues.append("defect SLA must be positive")
        return issues


@dataclass(frozen=True)
class ReleaseChecklist:
    release_stage: ReleaseStage
    checklist_path: str
    required_approvers: tuple[str, ...]
    evidence_bundle_required: bool
    known_issues_review_required: bool
    rollback_review_required: bool
    smoke_test_required: bool
    signoff_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.checklist_path.startswith("docs/testing/"):
            issues.append("release checklist must live under docs/testing/")
        if not self.required_approvers:
            issues.append("release checklist requires approvers")
        if not self.evidence_bundle_required:
            issues.append("release evidence bundle is required")
        if not self.known_issues_review_required:
            issues.append("known issues review is required")
        if not self.rollback_review_required:
            issues.append("rollback review is required")
        if not self.smoke_test_required:
            issues.append("smoke test is required")
        if self.release_stage in {ReleaseStage.BETA, ReleaseStage.PRODUCTION} and not self.signoff_required:
            issues.append("beta and production signoff is required")
        return issues


def compute_evidence_checksum(content: str) -> str:
    """Compute SHA-256 checksum for release evidence content."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_evidence_bundle(items: tuple[ReleaseEvidenceItem, ...], stage: ReleaseStage) -> list[str]:
    """Validate that a release evidence bundle has all required evidence for a stage."""

    issues: list[str] = []
    present = {item.evidence_type for item in items if item.required_for_stage == stage}
    required = {
        EvidenceType.TEST_REPORT,
        EvidenceType.COVERAGE_REPORT,
        EvidenceType.SECURITY_SCAN,
        EvidenceType.RELEASE_APPROVAL,
        EvidenceType.SMOKE_TEST_REPORT,
        EvidenceType.KNOWN_ISSUES_REGISTER,
    }
    if stage in {ReleaseStage.BETA, ReleaseStage.PRODUCTION}:
        for evidence_type in required:
            if evidence_type not in present:
                issues.append(f"missing {evidence_type.value} for {stage.value}")
    for item in items:
        issues.extend(item.validate())
    return issues


def summarize_gate_status(statuses: Mapping[str, QualityGateStatus]) -> QualityGateStatus:
    """Summarize multiple quality-gate statuses into one release-gate status."""

    values = set(statuses.values())
    if QualityGateStatus.FAIL in values:
        return QualityGateStatus.FAIL
    if QualityGateStatus.BLOCKED in values:
        return QualityGateStatus.BLOCKED
    if QualityGateStatus.WAIVED in values:
        return QualityGateStatus.WAIVED
    return QualityGateStatus.PASS


DEFAULT_TESTING_STRATEGY = TestingStrategyDecision(
    adr_path="docs/adr/ADR-014-testing-release-evidence-quality-gates.md",
    architecture_doc_path="docs/testing/testing_release_evidence_architecture_contract.md",
    pytest_required=True,
    frontend_test_required=True,
    contract_test_required=True,
    e2e_test_required=True,
    security_test_required=True,
    accessibility_test_required=True,
    performance_test_required=True,
    release_evidence_required=True,
)

DEFAULT_TEST_SUITES = (
    TestSuiteContract(TestLayer.UNIT, "pytest -c pytest.ini -q", "engineering", True, True, True, True, "test-results/unit.xml"),
    TestSuiteContract(TestLayer.INTEGRATION, "make integration-test", "engineering", True, True, True, True, "test-results/integration.xml"),
    TestSuiteContract(TestLayer.CONTRACT, "make openapi-check", "engineering", True, True, True, True, "docs/openapi.json"),
    TestSuiteContract(TestLayer.E2E, "make frontend-e2e", "frontend-owner", False, True, True, True, "test-results/e2e/"),
    TestSuiteContract(TestLayer.SECURITY, "make security-scan", "security-owner", True, True, True, True, "artifacts/security/scan.json"),
    TestSuiteContract(TestLayer.ACCESSIBILITY, "make frontend-accessibility-check", "frontend-owner", True, True, True, True, "artifacts/accessibility/report.json"),
    TestSuiteContract(TestLayer.PERFORMANCE, "make performance-smoke", "engineering", False, True, True, True, "artifacts/performance/report.json"),
    TestSuiteContract(TestLayer.SMOKE, "make staging-smoke", "release-owner", False, True, True, True, "artifacts/smoke/report.json"),
)

DEFAULT_COVERAGE_THRESHOLDS = (
    CoverageThreshold(TestLayer.UNIT, 75.0, 60.0, "coverage.xml", True, False),
    CoverageThreshold(TestLayer.INTEGRATION, 70.0, 50.0, "test-results/integration-coverage.xml", True, True),
)

DEFAULT_QUALITY_GATES = (
    QualityGate(
        "pull-request-quality-gate",
        ReleaseStage.PULL_REQUEST,
        (TestLayer.UNIT, TestLayer.INTEGRATION, TestLayer.CONTRACT, TestLayer.SECURITY, TestLayer.ACCESSIBILITY),
        (EvidenceType.TEST_REPORT, EvidenceType.COVERAGE_REPORT, EvidenceType.SECURITY_SCAN, EvidenceType.OPENAPI_ARTIFACT),
        False,
        "docs/testing/quality_gate_waiver_policy.md",
        True,
        "engineering",
    ),
    QualityGate(
        "beta-release-quality-gate",
        ReleaseStage.BETA,
        (TestLayer.UNIT, TestLayer.INTEGRATION, TestLayer.CONTRACT, TestLayer.E2E, TestLayer.SECURITY, TestLayer.ACCESSIBILITY, TestLayer.SMOKE),
        (EvidenceType.TEST_REPORT, EvidenceType.COVERAGE_REPORT, EvidenceType.SECURITY_SCAN, EvidenceType.RELEASE_APPROVAL, EvidenceType.SMOKE_TEST_REPORT, EvidenceType.KNOWN_ISSUES_REGISTER),
        True,
        "docs/testing/quality_gate_waiver_policy.md",
        True,
        "release-owner",
    ),
    QualityGate(
        "production-quality-gate",
        ReleaseStage.PRODUCTION,
        (TestLayer.UNIT, TestLayer.INTEGRATION, TestLayer.CONTRACT, TestLayer.E2E, TestLayer.SECURITY, TestLayer.ACCESSIBILITY, TestLayer.PERFORMANCE, TestLayer.SMOKE, TestLayer.REGRESSION),
        (EvidenceType.TEST_REPORT, EvidenceType.COVERAGE_REPORT, EvidenceType.SECURITY_SCAN, EvidenceType.ACCESSIBILITY_REPORT, EvidenceType.PERFORMANCE_REPORT, EvidenceType.RELEASE_APPROVAL, EvidenceType.SMOKE_TEST_REPORT, EvidenceType.KNOWN_ISSUES_REGISTER),
        True,
        "docs/testing/quality_gate_waiver_policy.md",
        True,
        "release-owner",
    ),
)

_SAMPLE_SHA = "abcdef1234567890"
DEFAULT_RELEASE_EVIDENCE = (
    ReleaseEvidenceItem("test-report-001", EvidenceType.TEST_REPORT, "test-results/unit.xml", "pytest", _SAMPLE_SHA, compute_evidence_checksum("unit-test-report"), ReleaseStage.BETA, True),
    ReleaseEvidenceItem("coverage-001", EvidenceType.COVERAGE_REPORT, "coverage.xml", "pytest-cov", _SAMPLE_SHA, compute_evidence_checksum("coverage-report"), ReleaseStage.BETA, True),
    ReleaseEvidenceItem("security-001", EvidenceType.SECURITY_SCAN, "artifacts/security/scan.json", "security-scan", _SAMPLE_SHA, compute_evidence_checksum("security-scan"), ReleaseStage.BETA, True),
    ReleaseEvidenceItem("approval-001", EvidenceType.RELEASE_APPROVAL, "docs/testing/beta_release_quality_gate_checklist.md", "release-owner", _SAMPLE_SHA, compute_evidence_checksum("release-approval"), ReleaseStage.BETA, True),
    ReleaseEvidenceItem("smoke-001", EvidenceType.SMOKE_TEST_REPORT, "artifacts/smoke/report.json", "staging-smoke", _SAMPLE_SHA, compute_evidence_checksum("smoke-report"), ReleaseStage.BETA, True),
    ReleaseEvidenceItem("known-issues-001", EvidenceType.KNOWN_ISSUES_REGISTER, "docs/testing/known_issues_release_register.md", "release-owner", _SAMPLE_SHA, compute_evidence_checksum("known-issues"), ReleaseStage.BETA, True),
)

DEFAULT_DEFECT_TRIAGE = (
    DefectTriageRule(DefectSeverity.LOW, False, True, True, 25, 240),
    DefectTriageRule(DefectSeverity.MEDIUM, False, True, True, 10, 120),
    DefectTriageRule(DefectSeverity.HIGH, True, True, True, 2, 48),
    DefectTriageRule(DefectSeverity.CRITICAL, True, True, True, 0, 24),
    DefectTriageRule(DefectSeverity.RELEASE_BLOCKER, True, True, True, 0, 8),
)

DEFAULT_RELEASE_CHECKLISTS = (
    ReleaseChecklist(ReleaseStage.BETA, "docs/testing/beta_release_quality_gate_checklist.md", ("release-owner", "engineering"), True, True, True, True, True),
    ReleaseChecklist(ReleaseStage.PRODUCTION, "docs/testing/production_release_quality_gate_checklist.md", ("release-owner", "engineering", "privacy"), True, True, True, True, True),
)


def default_quality_gate_readiness_report() -> dict[str, object]:
    """Return deterministic testing/release evidence quality-gate readiness evidence."""

    statuses = {
        "unit": QualityGateStatus.PASS,
        "integration": QualityGateStatus.PASS,
        "security": QualityGateStatus.PASS,
    }
    return {
        "strategy_issues": DEFAULT_TESTING_STRATEGY.validate(),
        "test_suite_issues": [issue for suite in DEFAULT_TEST_SUITES for issue in suite.validate()],
        "coverage_threshold_issues": [issue for threshold in DEFAULT_COVERAGE_THRESHOLDS for issue in threshold.validate()],
        "quality_gate_issues": [issue for gate in DEFAULT_QUALITY_GATES for issue in gate.validate()],
        "release_evidence_issues": [issue for item in DEFAULT_RELEASE_EVIDENCE for issue in item.validate()],
        "evidence_bundle_issues": validate_evidence_bundle(DEFAULT_RELEASE_EVIDENCE, ReleaseStage.BETA),
        "defect_triage_issues": [issue for rule in DEFAULT_DEFECT_TRIAGE for issue in rule.validate()],
        "release_checklist_issues": [issue for checklist in DEFAULT_RELEASE_CHECKLISTS for issue in checklist.validate()],
        "checksum_sample": compute_evidence_checksum("release-evidence"),
        "gate_status_sample": summarize_gate_status(statuses).value,
    }
