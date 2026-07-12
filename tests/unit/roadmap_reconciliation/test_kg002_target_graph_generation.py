from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.domain.knowledge_graph_target import build_target_graph, validate_target_graph
from scripts.roadmap_reconciliation.verify_kg002_target_graph_generation import evaluate


def _copy_repo(tmp_path: Path) -> Path:
    root = Path.cwd()
    dst = tmp_path / "repo"
    paths = [
        "data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json",
        "data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph_summary.json",
        "docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json",
        "docs/roadmap/knowledge_graph/kg_002_target_graph_generation.md",
        "docs/roadmap/knowledge_graph/kg_002_target_graph_generation_record.json",
        "docs/roadmap/knowledge_graph/kg_implementation_roadmap.md",
        "docs/roadmap/knowledge_graph/kg_roadmap_register.json",
        "docs/knowledge_graph/target_graph/kg002_target_graph_manifest.json",
        "docs/knowledge_graph/target_graph/kg002_target_graph_generation_policy.md",
        "docs/knowledge_graph/target_graph/kg002_target_graph_schema.md",
        "docs/knowledge_graph/target_graph/kg002_target_graph_policy_contract.md",
        "docs/knowledge_graph/target_graph/kg002_target_graph_review_manifest.json",
        "docs/knowledge_graph/target_graph/kg002_target_graph_runtime_boundary.md",
    ]
    for rel in paths:
        src = root / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    record_path = dst / "docs/roadmap/knowledge_graph/kg_002_target_graph_generation_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["target_graph_generation_recorded"] = False
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dst


def _mark_record_captured(repo: Path, graph: dict) -> None:
    record_path = repo / "docs" / "roadmap" / "knowledge_graph" / "kg_002_target_graph_generation_record.json"
    data = json.loads(record_path.read_text(encoding="utf-8"))
    data.update({
        "target_graph_generation_recorded": True,
        "kg1_caps_graph_foundation_valid": True,
        "caps_graph_dependency_recorded": True,
        "caps_graph_sha256": graph["source"]["caps_graph_sha256"],
        "target_graph_artifact_generated": True,
        "target_graph_schema_recorded": True,
        "target_graph_policy_contract_recorded": True,
        "target_graph_review_manifest_recorded": True,
        "target_graph_state_count": graph["counts"]["target_states"],
        "target_graph_edge_count": graph["counts"]["target_edges"],
        "target_graph_references_approved_caps_nodes_only": True,
        "required_mastery_thresholds_present": True,
        "required_confidence_thresholds_present": True,
        "priority_weighting_present": True,
        "pacing_windows_present": True,
        "duplicate_target_keys_found_false": True,
        "orphan_target_edges_found_false": True,
        "runtime_kg_boundary_recorded": True,
    })
    record_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_kg002_authority_is_valid_before_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    result = evaluate(repo)
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["target_graph_generation_recorded"] is False


def test_kg002_builds_valid_target_graph_from_caps_graph() -> None:
    graph = build_target_graph()
    validation = validate_target_graph(graph)
    assert validation["valid"] is True
    assert graph["counts"]["target_states"] >= 100
    assert graph["counts"]["target_prerequisite_edges"] >= 20


def test_kg002_requires_kg1_dependency(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    (repo / "docs" / "roadmap" / "knowledge_graph" / "kg_001_caps_graph_foundation_record.json").unlink()
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert result["kg1_caps_graph_foundation_valid"] is False


def test_kg002_boundary_flags_must_remain_false(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    record_path = repo / "docs" / "roadmap" / "knowledge_graph" / "kg_002_target_graph_generation_record.json"
    data = json.loads(record_path.read_text())
    data["target_graph_runtime_authority_authorised"] = True
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert any("target_graph_runtime_authority_authorised" in error for error in result["errors"])


def test_kg002_valid_after_target_graph_artifact_and_record(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    graph = build_target_graph(repo / "data" / "knowledge_graph" / "caps_graph_foundation" / "grade4_mathematics_caps_graph.json")
    artifact = repo / "data" / "knowledge_graph" / "target_graph" / "grade4_mathematics_target_graph.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = artifact.parent / "grade4_mathematics_target_graph_summary.json"
    summary.write_text(json.dumps({"valid": True, "counts": graph["counts"]}), encoding="utf-8")
    _mark_record_captured(repo, graph)
    result = evaluate(repo)
    assert result["valid"] is True
    assert result["target_graph_artifact_generated"] is True
    assert result["target_graph_references_approved_caps_nodes_only"] is True


def test_kg002_boundary_flags_are_emitted_as_false_values(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    graph = build_target_graph(repo / "data" / "knowledge_graph" / "caps_graph_foundation" / "grade4_mathematics_caps_graph.json")
    artifact = repo / "data" / "knowledge_graph" / "target_graph" / "grade4_mathematics_target_graph.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact.parent / "grade4_mathematics_target_graph_summary.json").write_text(json.dumps({"valid": True}), encoding="utf-8")
    _mark_record_captured(repo, graph)
    result = evaluate(repo)
    assert result["database_schema_migration_authorised"] is False
    assert result["runtime_kg_authority_switch_authorised"] is False
    assert result["target_graph_runtime_authority_authorised"] is False
    assert result["public_beta_authorised"] is False
