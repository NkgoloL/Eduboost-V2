from pathlib import Path

from app.domain.knowledge_graph_runtime_activation import (
    DEFAULT_KG7_READINESS_PACK,
    build_runtime_activation_pack,
    validate_runtime_activation_pack,
)
from scripts.roadmap_reconciliation.verify_kgact001_controlled_runtime_kg_authority_activation import evaluate


def test_kgact001_authority_valid_before_evidence_capture() -> None:
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["controlled_runtime_kg_authority_activation_recorded"] is True
    assert result["runtime_kg_authority_switch_authorised"] is True
    assert result["authority_switch_executed"] is True


def test_kgact001_builds_activation_pack_from_kg7_readiness() -> None:
    pack = build_runtime_activation_pack(DEFAULT_KG7_READINESS_PACK)
    validation = validate_runtime_activation_pack(pack)
    assert validation["valid"] is True
    assert validation["activation_control_count"] == 4
    assert validation["readiness_check_count_inherited"] >= 10
    assert validation["legacy_projection_mapping_count_inherited"] >= 700
    assert validation["runtime_kg_authority_switch_authorised"] is True
    assert validation["authority_switch_executed"] is True
    assert validation["production_release_authorised"] is False
    assert validation["deployment_authorised"] is False
    assert validation["public_beta_authorised"] is False


def test_kgact001_activation_pack_controls_are_source_grounded() -> None:
    pack = build_runtime_activation_pack(DEFAULT_KG7_READINESS_PACK)
    validation = validate_runtime_activation_pack(pack)
    assert validation["all_activation_controls_source_grounded"] is True
    assert validation["all_activation_edges_source_grounded"] is True
    assert validation["duplicate_activation_control_keys_found_false"] is True
    assert validation["orphan_activation_edges_found_false"] is True


def test_kgact001_boundaries_keep_release_and_deployment_false() -> None:
    pack = build_runtime_activation_pack(DEFAULT_KG7_READINESS_PACK)
    validation = validate_runtime_activation_pack(pack)
    assert validation["runtime_kg_implementation_claimed"] is True
    assert validation["runtime_kg_authority_switch_authorised"] is True
    assert validation["authority_switch_executed"] is True
    assert validation["database_schema_migration_authorised"] is False
    assert validation["learner_facing_model_change_authorised"] is False
    assert validation["production_release_authorised"] is False
    assert validation["billing_launch_authorised"] is False
