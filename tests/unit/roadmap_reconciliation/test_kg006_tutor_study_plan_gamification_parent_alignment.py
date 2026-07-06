from pathlib import Path

from app.domain.knowledge_graph_product_alignment import (
    DEFAULT_GENERATION_PACK,
    build_product_alignment_pack,
    validate_product_alignment_pack,
)
from scripts.roadmap_reconciliation.verify_kg006_tutor_study_plan_gamification_parent_alignment import evaluate


def test_kg006_authority_valid_before_evidence_capture() -> None:
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["product_alignment_recorded"] is False
    assert result["runtime_kg_implementation_claimed"] is False
    assert result["tutor_runtime_authority_authorised"] is False


def test_kg006_builds_product_alignment_pack_from_kg5_generation_pack() -> None:
    pack = build_product_alignment_pack(DEFAULT_GENERATION_PACK)
    validation = validate_product_alignment_pack(pack)
    assert validation["valid"] is True
    assert pack["counts"]["tutor_previews"] >= 200
    assert pack["counts"]["study_plan_items"] >= 200
    assert pack["counts"]["gamification_award_candidates"] >= 200
    assert pack["boundary"]["uses_live_learner_data"] is False


def test_kg006_product_alignment_pack_is_source_grounded_and_review_gated() -> None:
    pack = build_product_alignment_pack(DEFAULT_GENERATION_PACK)
    validation = validate_product_alignment_pack(pack)
    assert validation["all_tutor_previews_source_grounded"] is True
    assert validation["all_study_plan_items_source_grounded"] is True
    assert validation["all_gamification_candidates_source_grounded"] is True
    assert validation["all_parent_summaries_source_grounded"] is True
    assert validation["all_product_items_review_required"] is True


def test_kg006_product_alignment_pack_has_no_duplicate_or_orphan_records() -> None:
    pack = build_product_alignment_pack(DEFAULT_GENERATION_PACK)
    validation = validate_product_alignment_pack(pack)
    assert validation["duplicate_tutor_preview_keys_found_false"] is True
    assert validation["duplicate_study_plan_item_keys_found_false"] is True
    assert validation["duplicate_award_candidate_keys_found_false"] is True
    assert validation["duplicate_parent_summary_keys_found_false"] is True
    assert validation["orphan_product_edges_found_false"] is True


def test_kg006_product_alignment_pack_uses_synthetic_aliases_only() -> None:
    pack = build_product_alignment_pack(DEFAULT_GENERATION_PACK)
    validation = validate_product_alignment_pack(pack)
    assert validation["no_live_learner_aliases"] is True
    assert validation["all_parent_summaries_synthetic_only"] is True
    assert all(item["no_live_learner_data"] is True for item in pack["tutor_previews"])
    assert all(item["human_review_required"] is True for item in pack["gamification_award_candidates"])
