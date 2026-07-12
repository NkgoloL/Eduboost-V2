from pathlib import Path

from app.domain.knowledge_graph_post_switch_review import (
    DEFAULT_RUNTIME_ACTIVATION_PACK,
    build_post_switch_review_pack,
    validate_post_switch_review_pack,
)
from scripts.roadmap_reconciliation.verify_kg008_post_switch_optimisation_scale_review import evaluate


def test_kg008_authority_valid_before_evidence_capture() -> None:
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["post_switch_optimisation_scale_review_recorded"] is True
    assert result["kgact001_controlled_runtime_activation_valid"] is True


def test_kg008_builds_post_switch_review_pack_from_activation() -> None:
    pack = build_post_switch_review_pack(DEFAULT_RUNTIME_ACTIVATION_PACK)
    validation = validate_post_switch_review_pack(pack)
    assert validation["valid"] is True
    assert validation["optimisation_candidate_count"] == 8
    assert validation["scale_review_check_count"] == 10
    assert validation["monitoring_requirement_count"] == 8
    assert validation["rollback_observability_check_count"] == 6
    assert validation["post_switch_review_edge_count"] == 32


def test_kg008_review_pack_is_source_grounded_and_review_only() -> None:
    pack = build_post_switch_review_pack(DEFAULT_RUNTIME_ACTIVATION_PACK)
    validation = validate_post_switch_review_pack(pack)
    assert validation["all_optimisation_candidates_source_grounded"] is True
    assert validation["all_scale_review_checks_source_grounded"] is True
    assert validation["all_monitoring_requirements_source_grounded"] is True
    assert validation["all_rollback_observability_checks_source_grounded"] is True
    assert validation["all_post_switch_edges_source_grounded"] is True
    assert validation["all_post_switch_items_review_only"] is True


def test_kg008_boundaries_keep_launch_and_execution_false() -> None:
    pack = build_post_switch_review_pack(DEFAULT_RUNTIME_ACTIVATION_PACK)
    validation = validate_post_switch_review_pack(pack)
    assert validation["runtime_kg_implementation_claimed"] is True
    assert validation["runtime_kg_authority_switch_authorised"] is True
    assert validation["authority_switch_executed"] is True
    assert validation["optimisation_execution_authorised"] is False
    assert validation["scale_load_test_execution_authorised"] is False
    assert validation["production_release_authorised"] is False
    assert validation["deployment_authorised"] is False
    assert validation["public_beta_authorised"] is False
    assert validation["billing_launch_authorised"] is False
