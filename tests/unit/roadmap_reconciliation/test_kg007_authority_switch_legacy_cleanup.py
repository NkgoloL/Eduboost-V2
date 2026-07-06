from pathlib import Path

from app.domain.knowledge_graph_authority_switch import (
    DEFAULT_PRODUCT_ALIGNMENT_PACK,
    build_authority_switch_readiness_pack,
    validate_authority_switch_readiness_pack,
)
from scripts.roadmap_reconciliation.verify_kg007_authority_switch_legacy_cleanup import evaluate


def test_kg007_authority_valid_before_evidence_capture() -> None:
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["authority_switch_legacy_cleanup_recorded"] is False
    assert result["runtime_kg_authority_switch_authorised"] is False
    assert result["authority_switch_executed"] is False


def test_kg007_builds_authority_switch_readiness_pack_from_kg6_product_alignment() -> None:
    pack = build_authority_switch_readiness_pack(DEFAULT_PRODUCT_ALIGNMENT_PACK)
    validation = validate_authority_switch_readiness_pack(pack)
    assert validation["valid"] is True
    assert pack["counts"]["legacy_projection_mappings"] >= 700
    assert pack["counts"]["authority_readiness_checks"] >= 10
    assert pack["boundary"]["runtime_kg_authority_switch_authorised"] is False


def test_kg007_readiness_pack_is_source_grounded_and_readiness_only() -> None:
    pack = build_authority_switch_readiness_pack(DEFAULT_PRODUCT_ALIGNMENT_PACK)
    validation = validate_authority_switch_readiness_pack(pack)
    assert validation["all_legacy_projection_mappings_source_grounded"] is True
    assert validation["all_readiness_checks_source_grounded"] is True
    assert validation["all_cleanup_tasks_source_grounded"] is True
    assert validation["all_legacy_projection_mappings_readiness_only"] is True


def test_kg007_readiness_pack_has_no_duplicate_or_orphan_records() -> None:
    pack = build_authority_switch_readiness_pack(DEFAULT_PRODUCT_ALIGNMENT_PACK)
    validation = validate_authority_switch_readiness_pack(pack)
    assert validation["duplicate_readiness_check_keys_found_false"] is True
    assert validation["duplicate_legacy_projection_keys_found_false"] is True
    assert validation["duplicate_cleanup_task_keys_found_false"] is True
    assert validation["duplicate_rollback_control_keys_found_false"] is True
    assert validation["orphan_switch_edges_found_false"] is True


def test_kg007_boundaries_remain_false() -> None:
    pack = build_authority_switch_readiness_pack(DEFAULT_PRODUCT_ALIGNMENT_PACK)
    validation = validate_authority_switch_readiness_pack(pack)
    assert validation["runtime_kg_implementation_claimed"] is False
    assert validation["runtime_kg_authority_switch_authorised"] is False
    assert validation["database_schema_migration_authorised"] is False
    assert validation["learner_facing_model_change_authorised"] is False
    assert validation["production_release_authorised"] is False
