from tests.support.governance_state import (
    assert_archival_or_current_valid,
    assert_historical_next_with_current_execution,
)
from scripts.production_readiness.audit_prd900_904_billing_commercial_launch_readiness_foundation import audit


def test_prd900_904_authority_and_evidence_state_are_valid():
    result = audit()

    assert_archival_or_current_valid(result)
    assert result["previous_prd8_handoff_valid"] is True
    assert result["commercial_launch_readiness_valid"] is True
    assert result["billing_provider_test_mode_defined"] is True
    assert result["pricing_packaging_defined"] is True
    assert result["checkout_webhook_contract_defined"] is True
    assert result["subscription_entitlement_matrix_defined"] is True
    assert result["invoice_tax_refund_support_defined"] is True
    assert result["sponsorship_school_procurement_defined"] is True
    assert result["commercial_support_reconciliation_defined"] is True
    assert result["terms_privacy_launch_comms_defined"] is True
    assert result["prd10_implementation_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False

    assert result["commercial_launch_foundation_recorded"] is True
    assert result["commercial_launch_evidence_recorded"] is True
    assert_historical_next_with_current_execution(result, "PRD-9.5-9.9")
