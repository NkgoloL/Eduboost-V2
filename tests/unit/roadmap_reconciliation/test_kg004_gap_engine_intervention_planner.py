from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.domain.knowledge_graph_gap_engine import build_gap_intervention_plan, validate_gap_intervention_plan
from scripts.roadmap_reconciliation.verify_kg004_gap_engine_intervention_planner import evaluate


def _copy_repo(tmp_path: Path) -> Path:
    root = Path.cwd()
    dst = tmp_path / "repo"
    paths = [
        "data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json",
        "data/knowledge_graph/target_graph/grade4_mathematics_target_graph_summary.json",
        "data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph.json",
        "data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph_summary.json",
        "docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode_record.json",
        "docs/roadmap/knowledge_graph/kg_004_gap_engine_intervention_planner.md",
        "docs/roadmap/knowledge_graph/kg_004_gap_engine_intervention_planner_record.json",
        "docs/knowledge_graph/gap_engine/kg004_gap_engine_manifest.json",
        "docs/knowledge_graph/gap_engine/kg004_gap_engine_policy.md",
        "docs/knowledge_graph/gap_engine/kg004_gap_engine_schema.md",
        "docs/knowledge_graph/gap_engine/kg004_intervention_planner_contract.md",
        "docs/knowledge_graph/gap_engine/kg004_gap_engine_advisory_boundary.md",
        "docs/knowledge_graph/gap_engine/kg004_gap_engine_review_manifest.json",
    ]
    for rel in paths:
        src = root / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    # Tests should model the authority state before evidence capture even when
    # run from a later evidence-merged checkout.
    record_path = dst / "docs" / "roadmap" / "knowledge_graph" / "kg_004_gap_engine_intervention_planner_record.json"
    data = json.loads(record_path.read_text(encoding="utf-8"))
    for key in [
        "gap_engine_intervention_planner_recorded",
        "kg3_learner_graph_shadow_mode_valid",
        "shadow_graph_dependency_recorded",
        "target_graph_dependency_recorded",
        "gap_intervention_plan_artifact_generated",
        "synthetic_learner_fixture_only",
        "no_live_learner_data_used",
        "all_gap_items_reference_shadow_states",
        "all_gap_items_source_grounded",
        "all_interventions_source_grounded",
        "all_interventions_advisory_only",
        "duplicate_gap_keys_found_false",
        "duplicate_intervention_keys_found_false",
        "orphan_planner_edges_found_false",
    ]:
        data[key] = False
    record_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dst


def _mark_record_captured(repo: Path, plan: dict) -> None:
    record_path = repo / "docs" / "roadmap" / "knowledge_graph" / "kg_004_gap_engine_intervention_planner_record.json"
    data = json.loads(record_path.read_text(encoding="utf-8"))
    validation = validate_gap_intervention_plan(plan)
    data.update({
        "gap_engine_intervention_planner_recorded": True,
        "kg3_learner_graph_shadow_mode_valid": True,
        "shadow_graph_dependency_recorded": True,
        "target_graph_dependency_recorded": True,
        "gap_intervention_plan_artifact_generated": True,
        "synthetic_learner_fixture_only": True,
        "no_live_learner_data_used": True,
        "gap_item_count": plan["counts"]["gap_items"],
        "intervention_recommendation_count": plan["counts"]["intervention_recommendations"],
        "planner_edge_count": plan["counts"]["planner_edges"],
        "all_gap_items_reference_shadow_states": validation["all_gap_items_reference_shadow_states"],
        "all_gap_items_source_grounded": validation["all_gap_items_source_grounded"],
        "all_interventions_source_grounded": validation["all_interventions_source_grounded"],
        "all_interventions_advisory_only": validation["all_interventions_advisory"],
        "duplicate_gap_keys_found_false": validation["duplicate_gap_keys_found_false"],
        "duplicate_intervention_keys_found_false": validation["duplicate_intervention_keys_found_false"],
        "orphan_planner_edges_found_false": validation["orphan_planner_edges_found_false"],
        "advisory_boundary_recorded": True,
        "privacy_boundary_recorded": True,
        "runtime_kg_boundary_recorded": True,
    })
    record_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_kg004_authority_is_valid_before_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    result = evaluate(repo)
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["gap_engine_intervention_planner_recorded"] is False


def test_kg004_builds_valid_gap_intervention_plan() -> None:
    plan = build_gap_intervention_plan()
    validation = validate_gap_intervention_plan(plan)
    assert validation["valid"] is True
    assert plan["counts"]["gap_items"] >= 200
    assert plan["counts"]["intervention_recommendations"] == plan["counts"]["gap_items"]
    assert plan["boundary"]["advisory_only"] is True


def test_kg004_requires_kg3_dependency(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    (repo / "docs" / "roadmap" / "knowledge_graph" / "kg_003_learner_graph_shadow_mode_record.json").unlink()
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert result["kg3_learner_graph_shadow_mode_valid"] is False


def test_kg004_boundary_flags_must_remain_false(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    record_path = repo / "docs" / "roadmap" / "knowledge_graph" / "kg_004_gap_engine_intervention_planner_record.json"
    data = json.loads(record_path.read_text())
    data["intervention_planner_runtime_authority_authorised"] = True
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert any("intervention_planner_runtime_authority_authorised" in error for error in result["errors"])


def test_kg004_valid_after_plan_artifact_and_record(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    plan = build_gap_intervention_plan(
        repo / "data" / "knowledge_graph" / "learner_shadow_mode" / "grade4_mathematics_learner_shadow_graph.json",
        repo / "data" / "knowledge_graph" / "target_graph" / "grade4_mathematics_target_graph.json",
    )
    artifact = repo / "data" / "knowledge_graph" / "gap_engine" / "grade4_mathematics_gap_intervention_plan.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = artifact.parent / "grade4_mathematics_gap_intervention_plan_summary.json"
    summary.write_text(json.dumps({"valid": True, "counts": plan["counts"]}), encoding="utf-8")
    _mark_record_captured(repo, plan)
    result = evaluate(repo)
    assert result["valid"] is True
    assert result["gap_intervention_plan_artifact_generated"] is True
    assert result["all_interventions_advisory_only"] is True


def test_kg004_rejects_live_learner_data_boundary(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    shadow = repo / "data" / "knowledge_graph" / "learner_shadow_mode" / "grade4_mathematics_learner_shadow_graph.json"
    data = json.loads(shadow.read_text())
    data["boundary"]["no_live_learner_data"] = False
    shadow.write_text(json.dumps(data), encoding="utf-8")
    try:
        build_gap_intervention_plan(
            shadow,
            repo / "data" / "knowledge_graph" / "target_graph" / "grade4_mathematics_target_graph.json",
        )
    except ValueError as exc:
        assert "no live learner data" in str(exc)
    else:
        raise AssertionError("expected KG-4 to reject live learner data boundary")
