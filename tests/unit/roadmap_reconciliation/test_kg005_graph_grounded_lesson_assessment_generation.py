from pathlib import Path

from app.domain.knowledge_graph_grounded_generation import (
    DEFAULT_GAP_PLAN,
    DEFAULT_TARGET_GRAPH,
    build_graph_grounded_generation_pack,
    validate_graph_grounded_generation_pack,
)
from scripts.roadmap_reconciliation.verify_kg005_graph_grounded_lesson_assessment_generation import evaluate


def test_kg005_authority_valid_before_evidence_capture() -> None:
    result = evaluate(Path("."))
    assert result["authority_valid"] is True
    assert result["valid"] is True
    assert result["graph_grounded_generation_recorded"] is True
    assert result["runtime_kg_implementation_claimed"] is False
    assert result["llm_provider_call_authorised"] is False


def test_kg005_builds_generation_pack_from_kg4_plan() -> None:
    pack = build_graph_grounded_generation_pack(DEFAULT_GAP_PLAN, DEFAULT_TARGET_GRAPH)
    validation = validate_graph_grounded_generation_pack(pack)
    assert validation["valid"] is True
    assert pack["counts"]["lesson_drafts"] >= 200
    assert pack["counts"]["assessment_drafts"] >= 200
    assert pack["boundary"]["generation_preview_only"] is True
    assert pack["boundary"]["uses_live_learner_data"] is False


def test_kg005_generation_pack_is_source_grounded_and_review_gated() -> None:
    pack = build_graph_grounded_generation_pack(DEFAULT_GAP_PLAN, DEFAULT_TARGET_GRAPH)
    validation = validate_graph_grounded_generation_pack(pack)
    assert validation["all_lessons_reference_interventions"] is True
    assert validation["all_lessons_source_grounded"] is True
    assert validation["all_assessments_reference_lessons"] is True
    assert validation["all_assessments_source_grounded"] is True
    assert validation["all_generation_items_review_required"] is True


def test_kg005_generation_pack_has_no_duplicate_or_orphan_records() -> None:
    pack = build_graph_grounded_generation_pack(DEFAULT_GAP_PLAN, DEFAULT_TARGET_GRAPH)
    validation = validate_graph_grounded_generation_pack(pack)
    assert validation["duplicate_lesson_keys_found_false"] is True
    assert validation["duplicate_assessment_keys_found_false"] is True
    assert validation["orphan_generation_edges_found_false"] is True


def test_kg005_generation_pack_uses_synthetic_aliases_only() -> None:
    pack = build_graph_grounded_generation_pack(DEFAULT_GAP_PLAN, DEFAULT_TARGET_GRAPH)
    validation = validate_graph_grounded_generation_pack(pack)
    assert validation["no_live_learner_aliases"] is True
    assert all(item["no_live_learner_data"] is True for item in pack["lesson_drafts"])
    assert all(item["human_review_required"] is True for item in pack["assessment_drafts"])
