from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.domain.knowledge_graph_caps import build_caps_graph, validate_caps_graph
from scripts.roadmap_reconciliation.verify_kg001_caps_graph_foundation import evaluate


def _copy_repo(tmp_path: Path) -> Path:
    root = Path.cwd()
    dst = tmp_path / "repo"
    paths = [
        "data/caps/topic_maps/caps_topic_map_grade4_maths.json",
        "docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json",
        "docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation.md",
        "docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json",
        "docs/roadmap/knowledge_graph/kg_implementation_roadmap.md",
        "docs/roadmap/knowledge_graph/kg_roadmap_register.json",
        "docs/knowledge_graph/caps_graph/kg001_caps_graph_manifest.json",
        "docs/knowledge_graph/caps_graph/kg001_caps_graph_foundation_policy.md",
        "docs/knowledge_graph/caps_graph/kg001_caps_graph_schema.md",
        "docs/knowledge_graph/caps_graph/kg001_caps_graph_loader_contract.md",
        "docs/knowledge_graph/caps_graph/kg001_caps_graph_review_manifest.json",
        "docs/knowledge_graph/caps_graph/kg001_caps_graph_runtime_boundary.md",
    ]
    for rel in paths:
        src = root / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    record_path = dst / "docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["caps_graph_foundation_recorded"] = False
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dst


def _mark_record_captured(repo: Path, graph: dict) -> None:
    record_path = repo / "docs" / "roadmap" / "knowledge_graph" / "kg_001_caps_graph_foundation_record.json"
    data = json.loads(record_path.read_text(encoding="utf-8"))
    data.update({
        "caps_graph_foundation_recorded": True,
        "kg0_formal_roadmap_approval_valid": True,
        "caps_source_topic_map_present": True,
        "caps_source_checksum_recorded": True,
        "caps_source_sha256": graph["source"]["source_sha256"],
        "caps_graph_artifact_generated": True,
        "caps_graph_schema_recorded": True,
        "caps_graph_loader_contract_recorded": True,
        "caps_graph_review_manifest_recorded": True,
        "caps_graph_node_count": graph["counts"]["nodes"],
        "caps_graph_edge_count": graph["counts"]["edges"],
        "all_caps_nodes_source_grounded": True,
        "all_caps_edges_source_grounded": True,
        "duplicate_node_keys_found_false": True,
        "orphan_edges_found_false": True,
        "runtime_kg_boundary_recorded": True,
    })
    record_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_kg001_authority_is_valid_before_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    result = evaluate(repo)
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["caps_graph_foundation_recorded"] is False


def test_kg001_builds_valid_caps_graph_from_topic_map() -> None:
    graph = build_caps_graph()
    validation = validate_caps_graph(graph)
    assert validation["valid"] is True
    assert graph["counts"]["terms"] == 4
    assert graph["counts"]["nodes"] >= 150
    assert graph["counts"]["edges"] >= 150


def test_kg001_requires_kg0_dependency(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    (repo / "docs" / "roadmap" / "knowledge_graph" / "kg_000_formal_kg_roadmap_approval_record.json").unlink()
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert result["kg0_formal_roadmap_approval_valid"] is False


def test_kg001_boundary_flags_must_remain_false(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    record_path = repo / "docs" / "roadmap" / "knowledge_graph" / "kg_001_caps_graph_foundation_record.json"
    data = json.loads(record_path.read_text())
    data["runtime_kg_authority_switch_authorised"] = True
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert any("runtime_kg_authority_switch_authorised" in error for error in result["errors"])


def test_kg001_valid_after_graph_artifact_and_record(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    graph = build_caps_graph(repo / "data" / "caps" / "topic_maps" / "caps_topic_map_grade4_maths.json")
    artifact = repo / "data" / "knowledge_graph" / "caps_graph_foundation" / "grade4_mathematics_caps_graph.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = repo / "data" / "knowledge_graph" / "caps_graph_foundation" / "grade4_mathematics_caps_graph_summary.json"
    summary.write_text(json.dumps({"valid": True, "counts": graph["counts"]}), encoding="utf-8")
    _mark_record_captured(repo, graph)
    result = evaluate(repo)
    assert result["valid"] is True
    assert result["caps_graph_artifact_generated"] is True
    assert result["all_caps_nodes_source_grounded"] is True


def test_kg001_boundary_flags_are_emitted_as_false_values(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    graph = build_caps_graph(repo / "data" / "caps" / "topic_maps" / "caps_topic_map_grade4_maths.json")
    artifact = repo / "data" / "knowledge_graph" / "caps_graph_foundation" / "grade4_mathematics_caps_graph.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact.parent / "grade4_mathematics_caps_graph_summary.json").write_text(json.dumps({"valid": True}), encoding="utf-8")
    _mark_record_captured(repo, graph)
    result = evaluate(repo)
    assert result["database_schema_migration_authorised"] is False
    assert result["runtime_kg_authority_switch_authorised"] is False
    assert result["public_beta_authorised"] is False
