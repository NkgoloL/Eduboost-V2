"""Final security assurance helpers for PRD-6.5-6.9.

This module closes the PRD-6 security assurance stream by combining the
PRD-6.0-6.4 readiness contract with final evidence, external/independent
review status, and explicit handoff controls. It does not authorise PRD-7
implementation, live learner traffic, billing, deployment, release tags,
public beta, or production release.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.security_assurance.readiness import (
    SECURITY_EVIDENCE_AREAS,
    SecurityAssuranceReadinessReport,
    build_default_security_assurance_readiness_report,
)

PRD_ID = "PRD-6.5-6.9"
SOURCE_READINESS_PRD_ID = "PRD-6.0-6.4"
FINAL_ASSURANCE_CRITERIA = (
    "dast_api_fuzzing_evidence_accepted",
    "dependency_container_sbom_evidence_accepted",
    "secret_rotation_rate_limit_abuse_evidence_accepted",
    "critical_endpoint_authz_negative_tests_accepted",
    "external_or_independent_review_recorded",
    "prd6_final_reconciliation_recorded",
)


@dataclass(frozen=True)
class SecurityFinalEvidenceItem:
    """One final PRD-6 security evidence item."""

    area: str
    evidence_recorded: bool = False
    findings_triaged: bool = False
    high_severity_blockers_open: bool = True
    blocks_live_traffic: bool = True
    blocks_production_release: bool = True

    @property
    def accepted(self) -> bool:
        return all([
            self.area in SECURITY_EVIDENCE_AREAS,
            self.evidence_recorded,
            self.findings_triaged,
            not self.high_severity_blockers_open,
        ])

    def to_payload(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "evidence_recorded": self.evidence_recorded,
            "findings_triaged": self.findings_triaged,
            "high_severity_blockers_open": self.high_severity_blockers_open,
            "blocks_live_traffic": self.blocks_live_traffic,
            "blocks_production_release": self.blocks_production_release,
            "accepted": self.accepted,
        }


@dataclass(frozen=True)
class SecurityFinalAssuranceInputs:
    """Inputs for the deterministic PRD-6 final assurance view."""

    readiness_report: SecurityAssuranceReadinessReport
    final_evidence_items: tuple[SecurityFinalEvidenceItem, ...] = field(default_factory=tuple)
    external_or_independent_review_recorded: bool = False
    security_signoff_recorded: bool = False
    prd6_final_reconciliation_recorded: bool = False


@dataclass(frozen=True)
class SecurityFinalAssuranceReport:
    """Final security assurance report for PRD-6.5-6.9."""

    inputs: SecurityFinalAssuranceInputs

    @property
    def final_evidence_matrix_accepted(self) -> bool:
        expected = set(SECURITY_EVIDENCE_AREAS)
        actual = {item.area for item in self.inputs.final_evidence_items}
        return expected == actual and all(item.accepted for item in self.inputs.final_evidence_items)

    @property
    def dast_api_fuzzing_evidence_accepted(self) -> bool:
        areas = {"api_dast", "api_fuzzing"}
        return all(item.accepted for item in self.inputs.final_evidence_items if item.area in areas) and areas.issubset({item.area for item in self.inputs.final_evidence_items})

    @property
    def dependency_container_sbom_evidence_accepted(self) -> bool:
        areas = {"python_dependency_scan", "frontend_dependency_scan", "container_image_scan", "sbom_generation"}
        return all(item.accepted for item in self.inputs.final_evidence_items if item.area in areas) and areas.issubset({item.area for item in self.inputs.final_evidence_items})

    @property
    def operational_security_evidence_accepted(self) -> bool:
        areas = {"secret_rotation_drill", "rate_limit_abuse_test", "authz_negative_tests"}
        return all(item.accepted for item in self.inputs.final_evidence_items if item.area in areas) and areas.issubset({item.area for item in self.inputs.final_evidence_items})

    @property
    def external_review_evidence_accepted(self) -> bool:
        return any(item.area == "external_review_plan" and item.accepted for item in self.inputs.final_evidence_items)

    @property
    def accepted(self) -> bool:
        return all([
            self.inputs.readiness_report.ready,
            self.final_evidence_matrix_accepted,
            self.inputs.external_or_independent_review_recorded,
            self.inputs.security_signoff_recorded,
            self.inputs.prd6_final_reconciliation_recorded,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.readiness_report.ready:
            blockers.append("prd6_security_readiness_incomplete")
            blockers.extend(self.inputs.readiness_report.blockers)
        if not self.final_evidence_matrix_accepted:
            blockers.append("final_security_evidence_matrix_incomplete")
        if not self.dast_api_fuzzing_evidence_accepted:
            blockers.append("dast_api_fuzzing_evidence_incomplete")
        if not self.dependency_container_sbom_evidence_accepted:
            blockers.append("dependency_container_sbom_evidence_incomplete")
        if not self.operational_security_evidence_accepted:
            blockers.append("operational_security_evidence_incomplete")
        if not self.external_review_evidence_accepted:
            blockers.append("external_review_evidence_incomplete")
        if not self.inputs.external_or_independent_review_recorded:
            blockers.append("external_or_independent_review_not_recorded")
        if not self.inputs.security_signoff_recorded:
            blockers.append("security_signoff_not_recorded")
        if not self.inputs.prd6_final_reconciliation_recorded:
            blockers.append("prd6_final_reconciliation_not_recorded")
        return list(dict.fromkeys(blockers))

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.accepted:
            return [
                "capture_prd6_final_security_assurance_evidence",
                "handoff_to_prd7_observability_sre_incident_readiness",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        readiness_payload = self.inputs.readiness_report.to_payload()
        return {
            "prd_id": PRD_ID,
            "source_readiness_prd_id": SOURCE_READINESS_PRD_ID,
            "accepted": self.accepted,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "acceptance_criteria": list(FINAL_ASSURANCE_CRITERIA),
            "security_readiness": readiness_payload,
            "dast_api_fuzzing_evidence_accepted": self.dast_api_fuzzing_evidence_accepted,
            "dependency_container_sbom_evidence_accepted": self.dependency_container_sbom_evidence_accepted,
            "secret_rotation_rate_limit_abuse_evidence_accepted": self.operational_security_evidence_accepted,
            "critical_endpoint_authz_negative_tests_accepted": any(item.area == "authz_negative_tests" and item.accepted for item in self.inputs.final_evidence_items),
            "external_review_evidence_accepted": self.external_review_evidence_accepted,
            "final_evidence_matrix_accepted": self.final_evidence_matrix_accepted,
            "external_or_independent_review_recorded": self.inputs.external_or_independent_review_recorded,
            "security_signoff_recorded": self.inputs.security_signoff_recorded,
            "prd6_final_reconciliation_recorded": self.inputs.prd6_final_reconciliation_recorded,
            "final_evidence_items": [item.to_payload() for item in self.inputs.final_evidence_items],
            "prd6_sequence_complete": self.accepted,
            "prd7_handoff_ready": self.accepted,
            "prd7_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }


def default_security_final_evidence_items(accepted: bool = True) -> tuple[SecurityFinalEvidenceItem, ...]:
    """Return deterministic final security evidence items."""

    return tuple(
        SecurityFinalEvidenceItem(
            area=area,
            evidence_recorded=accepted,
            findings_triaged=accepted,
            high_severity_blockers_open=not accepted,
            blocks_live_traffic=True,
            blocks_production_release=True,
        )
        for area in SECURITY_EVIDENCE_AREAS
    )


def build_security_final_assurance_report(inputs: SecurityFinalAssuranceInputs) -> SecurityFinalAssuranceReport:
    """Build a final PRD-6 security assurance report."""

    return SecurityFinalAssuranceReport(inputs=inputs)


def build_default_security_final_assurance_report() -> SecurityFinalAssuranceReport:
    """Build the accepted default PRD-6.5-6.9 final assurance report."""

    return build_security_final_assurance_report(
        SecurityFinalAssuranceInputs(
            readiness_report=build_default_security_assurance_readiness_report(),
            final_evidence_items=default_security_final_evidence_items(accepted=True),
            external_or_independent_review_recorded=True,
            security_signoff_recorded=True,
            prd6_final_reconciliation_recorded=True,
        )
    )


def build_blocked_security_final_assurance_report() -> SecurityFinalAssuranceReport:
    """Build a blocked PRD-6 final assurance report for tests and safety checks."""

    return build_security_final_assurance_report(
        SecurityFinalAssuranceInputs(
            readiness_report=build_default_security_assurance_readiness_report(),
            final_evidence_items=default_security_final_evidence_items(accepted=False),
            external_or_independent_review_recorded=False,
            security_signoff_recorded=False,
            prd6_final_reconciliation_recorded=False,
        )
    )
