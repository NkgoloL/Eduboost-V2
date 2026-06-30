from __future__ import annotations

from scripts.diagnostic_item_bank_canonicality import (
    CANONICAL_TABLE,
    SUPPORTING_TABLE,
    UNRESOLVED_BLOCKER,
    write_status,
)


def test_policy_declares_diagnostic_items_runtime_required():
    status = write_status()
    assert status.decision == "diagnostic_items-runtime-required"
    assert CANONICAL_TABLE == "diagnostic_items"
    assert SUPPORTING_TABLE == "irt_items"
    assert UNRESOLVED_BLOCKER == "DIAG-SCORE-001"


def test_policy_detects_runtime_diagnostic_items_references():
    status = write_status()
    assert status.runtime_diagnostic_items_references


def test_policy_acceptance_does_not_close_diag_score():
    status = write_status()
    assert status.status == "diagnostic-item-bank-policy-accepted"
    assert status.unresolved_blocker == "DIAG-SCORE-001"


def test_status_writes_policy_artifacts():
    status = write_status()
    assert status.status == "diagnostic-item-bank-policy-accepted"
    assert status.policy_markers_present["decision: diagnostic_items-runtime-required"]
