"""Billing and commercial launch readiness helpers for PRD-9.0-9.4.

The helper exposes a deterministic readiness contract for commercial launch
without enabling billing launch, live payment processing, live learner traffic,
deployment, release tags, public beta, or production release. It builds on the
existing billing monetisation contracts but treats them as readiness evidence,
not as authority to process real money.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.billing.production_readiness_contracts import default_billing_readiness_report

PRD_ID = "PRD-9.0-9.4"
COMMERCIAL_LAUNCH_SCOPE_ITEMS = (
    "billing_provider_test_mode_readiness",
    "pricing_packaging_readiness",
    "checkout_webhook_contract_readiness",
    "subscription_entitlement_readiness",
    "invoice_tax_refund_support_readiness",
    "sponsorship_school_procurement_readiness",
    "commercial_support_reconciliation_readiness",
    "terms_privacy_launch_comms_readiness",
)
COMMERCIAL_EVIDENCE_AREAS = (
    "provider_test_mode_decision",
    "pricing_packaging_matrix",
    "checkout_webhook_dry_run_contract",
    "subscription_entitlement_matrix",
    "invoice_receipt_tax_policy",
    "refund_cancellation_dunning_policy",
    "sponsorship_school_procurement_path",
    "commercial_support_reconciliation_runbook",
    "terms_privacy_launch_comms_review",
)
COMMERCIAL_RELEASE_BOUNDARIES = {
    "prd10_implementation_authorised": False,
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "live_learner_traffic_authorised": False,
    "billing_launch_authorised": False,
    "live_payment_processing_authorised": False,
}


@dataclass(frozen=True)
class CommercialLaunchEvidenceControl:
    """One PRD-9.0-9.4 commercial readiness evidence area."""

    area: str
    owner_assigned: bool = False
    evidence_path_defined: bool = False
    test_mode_only: bool = True
    policy_or_runbook_defined: bool = False
    blocks_billing_launch: bool = True
    blocks_live_payment_processing: bool = True

    @property
    def ready(self) -> bool:
        return all([
            self.owner_assigned,
            self.evidence_path_defined,
            self.test_mode_only,
            self.policy_or_runbook_defined,
            self.blocks_billing_launch,
            self.blocks_live_payment_processing,
        ])

    def to_payload(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "owner_assigned": self.owner_assigned,
            "evidence_path_defined": self.evidence_path_defined,
            "test_mode_only": self.test_mode_only,
            "policy_or_runbook_defined": self.policy_or_runbook_defined,
            "blocks_billing_launch": self.blocks_billing_launch,
            "blocks_live_payment_processing": self.blocks_live_payment_processing,
            "ready": self.ready,
        }


@dataclass(frozen=True)
class CommercialLaunchReadinessInputs:
    """Inputs for the deterministic PRD-9 commercial launch readiness view."""

    billing_provider_test_mode_defined: bool = False
    pricing_packaging_defined: bool = False
    checkout_webhook_contract_defined: bool = False
    subscription_entitlement_matrix_defined: bool = False
    invoice_tax_refund_support_defined: bool = False
    sponsorship_school_procurement_defined: bool = False
    commercial_support_reconciliation_defined: bool = False
    terms_privacy_launch_comms_defined: bool = False
    existing_billing_contracts_valid: bool = False
    evidence_controls: tuple[CommercialLaunchEvidenceControl, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommercialLaunchReadinessReport:
    """PRD-9.0-9.4 billing and commercial launch readiness report."""

    inputs: CommercialLaunchReadinessInputs

    @property
    def evidence_matrix_ready(self) -> bool:
        expected = set(COMMERCIAL_EVIDENCE_AREAS)
        actual = {control.area for control in self.inputs.evidence_controls}
        return expected == actual and all(control.ready for control in self.inputs.evidence_controls)

    @property
    def billing_contract_readiness_defined(self) -> bool:
        return all([
            self.inputs.billing_provider_test_mode_defined,
            self.inputs.checkout_webhook_contract_defined,
            self.inputs.subscription_entitlement_matrix_defined,
            self.inputs.existing_billing_contracts_valid,
        ])

    @property
    def commercial_policy_readiness_defined(self) -> bool:
        return all([
            self.inputs.pricing_packaging_defined,
            self.inputs.invoice_tax_refund_support_defined,
            self.inputs.sponsorship_school_procurement_defined,
            self.inputs.terms_privacy_launch_comms_defined,
        ])

    @property
    def support_reconciliation_defined(self) -> bool:
        return self.inputs.commercial_support_reconciliation_defined

    @property
    def ready(self) -> bool:
        return all([
            self.billing_contract_readiness_defined,
            self.commercial_policy_readiness_defined,
            self.support_reconciliation_defined,
            self.evidence_matrix_ready,
        ])

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.inputs.billing_provider_test_mode_defined:
            blockers.append("billing_provider_test_mode_missing")
        if not self.inputs.pricing_packaging_defined:
            blockers.append("pricing_packaging_missing")
        if not self.inputs.checkout_webhook_contract_defined:
            blockers.append("checkout_webhook_contract_missing")
        if not self.inputs.subscription_entitlement_matrix_defined:
            blockers.append("subscription_entitlement_matrix_missing")
        if not self.inputs.invoice_tax_refund_support_defined:
            blockers.append("invoice_tax_refund_support_missing")
        if not self.inputs.sponsorship_school_procurement_defined:
            blockers.append("sponsorship_school_procurement_missing")
        if not self.inputs.commercial_support_reconciliation_defined:
            blockers.append("commercial_support_reconciliation_missing")
        if not self.inputs.terms_privacy_launch_comms_defined:
            blockers.append("terms_privacy_launch_comms_missing")
        if not self.inputs.existing_billing_contracts_valid:
            blockers.append("existing_billing_contracts_not_valid")
        if not self.evidence_matrix_ready:
            blockers.append("commercial_evidence_matrix_incomplete")
        return blockers

    @property
    def recommended_next_actions(self) -> list[str]:
        if self.ready:
            return [
                "capture_prd9_commercial_launch_readiness_foundation_evidence",
                "continue_to_prd9_final_commercial_assurance_without_enabling_live_payments",
            ]
        return [f"resolve_{blocker}" for blocker in self.blockers]

    def to_payload(self) -> dict[str, Any]:
        billing_contracts = default_billing_readiness_report()
        return {
            "prd_id": PRD_ID,
            "ready": self.ready,
            "blockers": self.blockers,
            "recommended_next_actions": self.recommended_next_actions,
            "commercial_launch_scope_items": list(COMMERCIAL_LAUNCH_SCOPE_ITEMS),
            "commercial_evidence_areas": list(COMMERCIAL_EVIDENCE_AREAS),
            "billing_contracts": billing_contracts,
            "billing_contract_readiness_defined": self.billing_contract_readiness_defined,
            "commercial_policy_readiness_defined": self.commercial_policy_readiness_defined,
            "support_reconciliation_defined": self.support_reconciliation_defined,
            "evidence_matrix_ready": self.evidence_matrix_ready,
            "billing_provider_test_mode_defined": self.inputs.billing_provider_test_mode_defined,
            "pricing_packaging_defined": self.inputs.pricing_packaging_defined,
            "checkout_webhook_contract_defined": self.inputs.checkout_webhook_contract_defined,
            "subscription_entitlement_matrix_defined": self.inputs.subscription_entitlement_matrix_defined,
            "invoice_tax_refund_support_defined": self.inputs.invoice_tax_refund_support_defined,
            "sponsorship_school_procurement_defined": self.inputs.sponsorship_school_procurement_defined,
            "commercial_support_reconciliation_defined": self.inputs.commercial_support_reconciliation_defined,
            "terms_privacy_launch_comms_defined": self.inputs.terms_privacy_launch_comms_defined,
            "existing_billing_contracts_valid": self.inputs.existing_billing_contracts_valid,
            "evidence_controls": [control.to_payload() for control in self.inputs.evidence_controls],
            **COMMERCIAL_RELEASE_BOUNDARIES,
        }


def default_commercial_launch_evidence_controls(
    ready: bool = True,
) -> tuple[CommercialLaunchEvidenceControl, ...]:
    return tuple(
        CommercialLaunchEvidenceControl(
            area=area,
            owner_assigned=ready,
            evidence_path_defined=ready,
            test_mode_only=True,
            policy_or_runbook_defined=ready,
            blocks_billing_launch=True,
            blocks_live_payment_processing=True,
        )
        for area in COMMERCIAL_EVIDENCE_AREAS
    )


def _existing_billing_contracts_valid() -> bool:
    report = default_billing_readiness_report()
    return all([
        report.get("provider_decision_issues") == [],
        report.get("pricing_policy_issues") == [],
        report.get("retry_policy_issues") == [],
        report.get("signature_verification_sample") is True,
        report.get("state_transition_sample") is True,
    ])


def build_default_commercial_launch_readiness_report() -> CommercialLaunchReadinessReport:
    return CommercialLaunchReadinessReport(
        CommercialLaunchReadinessInputs(
            billing_provider_test_mode_defined=True,
            pricing_packaging_defined=True,
            checkout_webhook_contract_defined=True,
            subscription_entitlement_matrix_defined=True,
            invoice_tax_refund_support_defined=True,
            sponsorship_school_procurement_defined=True,
            commercial_support_reconciliation_defined=True,
            terms_privacy_launch_comms_defined=True,
            existing_billing_contracts_valid=_existing_billing_contracts_valid(),
            evidence_controls=default_commercial_launch_evidence_controls(),
        )
    )


def build_blocked_commercial_launch_readiness_report() -> CommercialLaunchReadinessReport:
    return CommercialLaunchReadinessReport(
        CommercialLaunchReadinessInputs(
            evidence_controls=default_commercial_launch_evidence_controls(ready=False),
        )
    )
