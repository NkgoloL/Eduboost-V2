"""Security assurance readiness helpers for PRD-6.0-6.4.

These helpers provide a deterministic, application-visible security assurance
contract. They model the readiness evidence required before EduBoost can move
towards external security review and later live learner traffic. They do not run
security scanners, modify branch protection, authorise PRD-7 implementation, or
authorise production release/deployment/public beta/billing/live traffic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRD_ID = "PRD-6.0-6.4"
SECURITY_SCOPE_ITEMS = (
    "dast_api_fuzzing_readiness",
    "dependency_and_container_scanning_readiness",
    "sbom_generation_readiness",
    "secret_rotation_drill_readiness",
    "rate_limit_and_abuse_testing_readiness",
    "external_security_review_path_readiness",
)
SECURITY_EVIDENCE_AREAS = (
    "api_dast",
    "api_fuzzing",
    "python_dependency_scan",
    "frontend_dependency_scan",
    "container_image_scan",
    "sbom_generation",
    "secret_rotation_drill",
    "rate_limit_abuse_test",
    "authz_negative_tests",
    "external_review_plan",
)
RECOMMENDED_TOOLS = (
    "bandit",
    "pip-audit",
    "pnpm_audit_or_equivalent",
    "container_image_scanner",
    "cyclonedx_or_syft_sbom",
    "owasp_zap_or_equivalent_dast",
    "api_fuzzing_harness",
)


@dataclass(frozen=True)
class SecurityEvidenceControl:
    """One security evidence area and its readiness controls."""

    area: str
    owner_assigned: bool = False
    tool_or_method_defined: bool = False
    evidence_path_defined: bool = False
    blocks_live_traffic: bool = True

    @property
    def ready(self) -> bool:
        return all([
            self.owner_assigned,
            self.tool_or_method_defined,
            self.evidence_path_defined,
        ])

    def to_payload(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "owner_assigned": self.owner_assigned,
            "tool_or_method_defined": self.tool_or_method_defined,
            "evidence_path_defined": self.evidence_path_defined,
            "blocks_live_traffic": self.blocks_live_traffic,
            "ready": self.ready,
        }


@dataclass(frozen=True)
class SecurityAssuranceReadinessInputs:
    """Inputs for the deterministic PRD-6 security assurance readiness view."""

    dast_api_fuzzing_plan_defined: bool = False
    dependency_scanning_plan_defined: bool = False
    container_image_scanning_plan_defined: bool = False
    sbom_generation_plan_defined: bool = False
    secret_rotation_drill_defined: bool = False
    rate_limit_abuse_testing_defined: bool = False
    external_review_path_defined: bool = False
    critical_endpoint_authz_tests_defined: bool = False
    evidence_controls: tuple[SecurityEvidenceControl, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SecurityAssuranceReadinessReport:
    """PRD-6.0-6.4 security assurance readiness report."""

    inputs: SecurityAssuranceReadinessInputs

    @property
    def evidence_matrix_ready(self) -> bool:
        expected = set(SECURITY_EVIDENCE_AREAS)
        actual = {control.area for control in self.inputs.evidence_controls}
        return expected == actual and all(control.ready for control in self.inputs.evidence_controls)

    @property
    def scanner_readiness_defined(self) -> bool:
        return all([
            self.inputs.dast_api_fuzzing_plan_defined,
            self.inputs.dependency_scanning_plan_defined,
            self.inputs.container_image_scanning_plan_defined,
            self.inputs.sbom_generation_plan_defined,
        ])

    @property
    def operational_security_drills_defined(self) -> bool:
        return all([
            self.inputs.secret_rotation_drill_defined,
            self.inputs.rate_limit_abuse_testing_defined,
            self.inputs.critical_endpoint_authz_tests_defined,
        ])

    @property
    def ready(self) -> bool:
        return all([
            self.scanner_readiness_defined,
            self.operational_security_drills_defined,
            self.inputs.external_review_path_defined,
            self.evidence_matrix_ready,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.dast_api_fuzzing_plan_defined:
            blockers.append("dast_api_fuzzing_plan_missing")
        if not self.inputs.dependency_scanning_plan_defined:
            blockers.append("dependency_scanning_plan_missing")
        if not self.inputs.container_image_scanning_plan_defined:
            blockers.append("container_image_scanning_plan_missing")
        if not self.inputs.sbom_generation_plan_defined:
            blockers.append("sbom_generation_plan_missing")
        if not self.inputs.secret_rotation_drill_defined:
            blockers.append("secret_rotation_drill_missing")
        if not self.inputs.rate_limit_abuse_testing_defined:
            blockers.append("rate_limit_abuse_testing_plan_missing")
        if not self.inputs.critical_endpoint_authz_tests_defined:
            blockers.append("critical_endpoint_authz_tests_missing")
        if not self.inputs.external_review_path_defined:
            blockers.append("external_review_path_missing")
        if not self.evidence_matrix_ready:
            blockers.append("security_evidence_matrix_incomplete")
        return blockers

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.ready:
            return [
                "capture_prd6_security_assurance_foundation_evidence",
                "prepare_prd6_final_external_review_handoff",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": PRD_ID,
            "ready": self.ready,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "scope_items": list(SECURITY_SCOPE_ITEMS),
            "security_evidence_areas": list(SECURITY_EVIDENCE_AREAS),
            "recommended_tools": list(RECOMMENDED_TOOLS),
            "dast_api_fuzzing_plan_defined": self.inputs.dast_api_fuzzing_plan_defined,
            "dependency_scanning_plan_defined": self.inputs.dependency_scanning_plan_defined,
            "container_image_scanning_plan_defined": self.inputs.container_image_scanning_plan_defined,
            "sbom_generation_plan_defined": self.inputs.sbom_generation_plan_defined,
            "secret_rotation_drill_defined": self.inputs.secret_rotation_drill_defined,
            "rate_limit_abuse_testing_defined": self.inputs.rate_limit_abuse_testing_defined,
            "critical_endpoint_authz_tests_defined": self.inputs.critical_endpoint_authz_tests_defined,
            "external_review_path_defined": self.inputs.external_review_path_defined,
            "scanner_readiness_defined": self.scanner_readiness_defined,
            "operational_security_drills_defined": self.operational_security_drills_defined,
            "evidence_matrix_ready": self.evidence_matrix_ready,
            "evidence_controls": [control.to_payload() for control in self.inputs.evidence_controls],
            "prd7_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }


def default_security_evidence_controls(ready: bool = True) -> tuple[SecurityEvidenceControl, ...]:
    """Return deterministic PRD-6 security evidence controls."""

    return tuple(
        SecurityEvidenceControl(
            area=area,
            owner_assigned=ready,
            tool_or_method_defined=ready,
            evidence_path_defined=ready,
            blocks_live_traffic=True,
        )
        for area in SECURITY_EVIDENCE_AREAS
    )


def build_security_assurance_readiness_report(
    inputs: SecurityAssuranceReadinessInputs,
) -> SecurityAssuranceReadinessReport:
    """Build a PRD-6 security assurance readiness report."""

    return SecurityAssuranceReadinessReport(inputs=inputs)


def build_default_security_assurance_readiness_report() -> SecurityAssuranceReadinessReport:
    """Build the accepted default PRD-6.0-6.4 security readiness report."""

    return build_security_assurance_readiness_report(
        SecurityAssuranceReadinessInputs(
            dast_api_fuzzing_plan_defined=True,
            dependency_scanning_plan_defined=True,
            container_image_scanning_plan_defined=True,
            sbom_generation_plan_defined=True,
            secret_rotation_drill_defined=True,
            rate_limit_abuse_testing_defined=True,
            external_review_path_defined=True,
            critical_endpoint_authz_tests_defined=True,
            evidence_controls=default_security_evidence_controls(ready=True),
        )
    )


def build_blocked_security_assurance_readiness_report() -> SecurityAssuranceReadinessReport:
    """Build a blocked PRD-6 readiness report for tests and safety checks."""

    return build_security_assurance_readiness_report(SecurityAssuranceReadinessInputs())
