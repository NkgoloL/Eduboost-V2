from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.domain.knowledge_graph_learner_shadow import build_learner_shadow_graph, validate_learner_shadow_graph
from scripts.roadmap_reconciliation.verify_kg003_learner_graph_shadow_mode import evaluate


def _copy_repo(tmp_path: Path) -> Path:
    root = Path.cwd()
    dst = tmp_path / "repo"
    paths = [
        "data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json",
        "data/knowledge_graph/target_graph/grade4_mathematics_target_graph_summary.json",
        "data/knowledge_graph/learner_shadow_mode/kg003_shadow_observation_fixture.json",
        "docs/roadmap/knowledge_graph/kg_002_target_graph_generation_record.json",
        "docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode.md",
        "docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode_record.json",
        "docs/knowledge_graph/learner_shadow/kg003_learner_graph_manifest.json",
        "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_policy.md",
        "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_schema.md",
        "docs/knowledge_graph/learner_shadow/kg003_shadow_observation_fixture_contract.md",
        "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_privacy_boundary.md",
        "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_runtime_boundary.md",
        "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_review_manifest.json",
    ]
    for rel in paths:
        src = root / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    record_path = dst / "docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["learner_graph_shadow_mode_recorded"] = False
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dst


def _mark_record_captured(repo: Path, graph: dict) -> None:
    record_path = repo / "docs" / "roadmap" / "knowledge_graph" / "kg_003_learner_graph_shadow_mode_record.json"
    data = json.loads(record_path.read_text(encoding="utf-8"))
    data.update({
        "learner_graph_shadow_mode_recorded": True,
        "kg2_target_graph_generation_valid": True,
        "target_graph_dependency_recorded": True,
        "shadow_observation_fixture_recorded": True,
        "learner_shadow_graph_artifact_generated": True,
        "synthetic_learner_fixture_only": True,
        "no_live_learner_data_used": True,
        "learner_shadow_state_count": graph["counts"]["learner_shadow_states"],
        "shadow_evidence_event_count": graph["counts"]["shadow_evidence_events"],
        "shadow_edge_count": graph["counts"]["shadow_edges"],
        "all_shadow_states_reference_targets": True,
        "all_shadow_states_source_grounded": True,
        "all_shadow_events_source_grounded": True,
        "duplicate_shadow_state_keys_found_false": True,
        "orphan_shadow_edges_found_false": True,
        "shadow_mode_boundary_recorded": True,
        "privacy_boundary_recorded": True,
        "runtime_kg_boundary_recorded": True,
    })
    record_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_kg003_authority_is_valid_before_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    result = evaluate(repo)
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["learner_graph_shadow_mode_recorded"] is False


def test_kg003_builds_valid_shadow_graph() -> None:
    graph = build_learner_shadow_graph()
    validation = validate_learner_shadow_graph(graph)
    assert validation["valid"] is True
    assert graph["counts"]["synthetic_learners"] == 2
    assert graph["counts"]["learner_shadow_states"] >= 200
    assert graph["boundary"]["runtime_kg_authority_switch_authorised"] is False


def test_kg003_requires_kg2_dependency(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    (repo / "docs" / "roadmap" / "knowledge_graph" / "kg_002_target_graph_generation_record.json").unlink()
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert result["kg2_target_graph_generation_valid"] is False


def test_kg003_boundary_flags_must_remain_false(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    record_path = repo / "docs" / "roadmap" / "knowledge_graph" / "kg_003_learner_graph_shadow_mode_record.json"
    data = json.loads(record_path.read_text())
    data["learner_graph_runtime_authority_authorised"] = True
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert any("learner_graph_runtime_authority_authorised" in error for error in result["errors"])


def test_kg003_valid_after_shadow_graph_artifact_and_record(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    graph = build_learner_shadow_graph(
        repo / "data" / "knowledge_graph" / "target_graph" / "grade4_mathematics_target_graph.json",
        repo / "data" / "knowledge_graph" / "learner_shadow_mode" / "kg003_shadow_observation_fixture.json",
    )
    artifact = repo / "data" / "knowledge_graph" / "learner_shadow_mode" / "grade4_mathematics_learner_shadow_graph.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = artifact.parent / "grade4_mathematics_learner_shadow_graph_summary.json"
    summary.write_text(json.dumps({"valid": True, "counts": graph["counts"]}), encoding="utf-8")
    _mark_record_captured(repo, graph)
    result = evaluate(repo)
    assert result["valid"] is True
    assert result["learner_shadow_graph_artifact_generated"] is True
    assert result["synthetic_learner_fixture_only"] is True


def test_kg003_shadow_graph_rejects_non_synthetic_alias(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    fixture = repo / "data" / "knowledge_graph" / "learner_shadow_mode" / "kg003_shadow_observation_fixture.json"
    data = json.loads(fixture.read_text())
    data["synthetic_learners"][0]["learner_alias"] = "real-learner-123"
    fixture.write_text(json.dumps(data), encoding="utf-8")
    try:
        build_learner_shadow_graph(
            repo / "data" / "knowledge_graph" / "target_graph" / "grade4_mathematics_target_graph.json",
            fixture,
        )
    except ValueError as exc:
        assert "synthetic" in str(exc)
    else:
        raise AssertionError("expected non-synthetic learner alias to be rejected")
