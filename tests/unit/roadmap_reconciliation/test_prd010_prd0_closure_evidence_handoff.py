from __future__ import annotations

from pathlib import Path

from scripts.production_readiness.audit_prd010_prd0_closure_evidence_handoff import closure_snapshot
from scripts.roadmap_reconciliation.verify_prd010_prd0_closure_evidence_handoff import evaluate

ROOT = Path(__file__).resolve().parents[3]


def test_prd010_authority_valid_after_apply() -> None:
    result = evaluate(ROOT)
    assert result["authority_valid"] is True
    assert result["prd009_repository_hygiene_generated_local_artifact_audit_valid"] is True
    assert result["all_prd0_predecessors_valid"] is True
    assert result["no_prd1_implementation_performed"] is True


def test_prd010_keeps_release_and_live_boundaries_closed() -> None:
    result = evaluate(ROOT)
    assert result["production_release_authorised"] is False
    assert result["deployment_authorised"] is False
    assert result["release_tag_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["live_learner_traffic_authorised"] is False
    assert result["billing_launch_authorised"] is False
    assert result["live_payment_processing_authorised"] is False
    assert result["new_kg_slice_authorised"] is False
    assert result["prd1_implementation_authorised"] is False


def test_prd010_snapshot_records_full_prd0_chain() -> None:
    snapshot = closure_snapshot(ROOT)
    assert snapshot["schema_version"] == "prd0-closure-evidence-handoff/v1"
    assert snapshot["prd_id"] == "PRD-0.10"
    assert snapshot["all_prd0_predecessors_valid"] is True
    assert list(snapshot["prd0_verifier_results"].keys()) == [f"PRD-0.{idx}" for idx in range(10)]


def test_prd010_handoff_target_is_terminal_prd0_or_prd1() -> None:
    result = evaluate(ROOT)
    assert result["register_next_authorised_item"] in {"PRD-0.10", "PRD-1"}
    if result["valid"]:
        assert result["register_next_authorised_item"] == "PRD-1"
        assert result["prd1_handoff_ready"] is True
