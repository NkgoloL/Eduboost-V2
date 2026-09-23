"""Unit tests for Full CAPS Curriculum Knowledge Graph and Proof Harness."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.domain.knowledge_graph_caps import (
    FULL_CURRICULUM_GRAPH_ID,
    FULL_CURRICULUM_GRAPH_VERSION,
    build_caps_graph,
    build_whole_curriculum_caps_graph,
    check_prerequisite_dag_acyclic,
    validate_caps_graph,
    verify_graph_artifact_version,
)
from scripts.knowledge_graph.prove_caps_curriculum_mapping import run_curriculum_mapping_proof


def test_build_whole_curriculum_caps_graph_structure():
    graph = build_whole_curriculum_caps_graph()
    assert graph["graph_id"] == FULL_CURRICULUM_GRAPH_ID
    assert graph["graph_version"] == FULL_CURRICULUM_GRAPH_VERSION
    assert graph["schema_version"] == "1.0"
    assert graph["counts"]["scopes"] == 51
    assert graph["counts"]["terms"] == 204
    assert graph["counts"]["topics"] == 823
    assert graph["counts"]["subtopics"] == 840
    assert graph["counts"]["assessment_statements"] == 2532
    assert graph["counts"]["misconceptions"] == 1690
    assert graph["counts"]["prerequisite_edges"] == 795
    assert graph["counts"]["cross_grade_progression_edges"] == 42
    assert graph["counts"]["nodes"] == 6152
    assert graph["counts"]["edges"] == 6988

    # Verify root nodes and phases exist
    node_keys = {n["node_key"] for n in graph["nodes"]}
    assert "caps:curriculum" in node_keys
    assert "caps:phase:foundation" in node_keys
    assert "caps:phase:intermediate" in node_keys
    assert "caps:phase:senior" in node_keys
    for g in range(8):
        assert f"caps:grade:{g}" in node_keys


def test_validate_caps_graph_passes_cleanly():
    graph = build_whole_curriculum_caps_graph()
    res = validate_caps_graph(graph)
    assert res["valid"] is True
    assert res["node_count"] == 6152
    assert res["edge_count"] == 6988


def test_prerequisite_dag_acyclicity_proof():
    graph = build_whole_curriculum_caps_graph()
    is_dag, cycle_nodes = check_prerequisite_dag_acyclic(graph["edges"])
    assert is_dag is True
    assert len(cycle_nodes) == 0


def test_prerequisite_dag_cycle_injection_detection():
    synthetic_edges = [
        {"source_node_key": "A", "target_node_key": "B", "edge_type": "prerequisite_of"},
        {"source_node_key": "B", "target_node_key": "C", "edge_type": "prerequisite_of"},
        {"source_node_key": "C", "target_node_key": "A", "edge_type": "prerequisite_of"},
    ]
    is_dag, cycle_nodes = check_prerequisite_dag_acyclic(synthetic_edges)
    assert is_dag is False
    assert len(cycle_nodes) > 0


def test_authoritative_mapping_proof_runner(tmp_path: Path):
    proof_file = tmp_path / "test_proof.json"
    proof = run_curriculum_mapping_proof(output_proof=proof_file)

    assert proof["verified"] is True
    assert proof["coverage_percentage"] == 100.0
    assert proof["curriculum_scope_proof"]["all_51_scopes_mapped"] is True
    assert proof["mathematical_graph_properties"]["orphan_edges_count"] == 0
    assert proof["mathematical_graph_properties"]["cycles_detected"] == 0
    assert proof["mathematical_graph_properties"]["boundary_isolation_verified"] is True
    assert proof_file.exists()


def test_individual_scope_graph_build():
    tm_file = Path("data/caps/topic_maps/grade7_coding_and_robotics_en.json")
    scope_graph = build_caps_graph(tm_file)
    assert scope_graph["scope"]["grade"] == 7
    assert scope_graph["scope"]["subject"] == "coding and robotics"
    assert scope_graph["counts"]["terms"] == 4
    assert scope_graph["counts"]["topics"] >= 1
    assert scope_graph["counts"]["nodes"] > 20
    validation = validate_caps_graph(scope_graph)
    assert validation["valid"] is True


def test_cross_grade_progression_edges_exist_and_acyclic():
    graph = build_whole_curriculum_caps_graph()
    prog_edges = [e for e in graph["edges"] if e.get("edge_type") == "progresses_to"]
    assert len(prog_edges) >= 1
    assert len(prog_edges) == 42

    # Assert strictly forward progression (lower to higher grade)
    for e in prog_edges:
        src_g = e.get("metadata", {}).get("source_grade")
        tgt_g = e.get("metadata", {}).get("target_grade")
        assert src_g is not None and tgt_g is not None
        assert src_g < tgt_g, f"Progression edge does not advance grade: {src_g} -> {tgt_g}"

    is_dag, cycles = check_prerequisite_dag_acyclic(graph["edges"])
    assert is_dag is True
    assert len(cycles) == 0


def test_graph_versioning_and_metadata():
    graph = build_whole_curriculum_caps_graph()
    assert graph.get("graph_version") == "2.0.0"
    assert graph.get("schema_version") == "1.0"
    assert graph.get("graph_sha256") is not None
    assert len(graph["graph_sha256"]) == 64
    assert verify_graph_artifact_version(graph, "2.0.0") is True
    assert verify_graph_artifact_version(graph, "1.0.0") is False


def test_knowledge_graph_loading_performance_benchmark():
    import time
    graph_path = Path("data/knowledge_graph/caps_graph_foundation/all_caps_curriculum_graph.json")
    assert graph_path.exists()

    # Multi-sample benchmark to eliminate transient scheduling jitter
    timings: list[float] = []
    data: dict[str, Any] = {}
    for _ in range(3):
        t0 = time.perf_counter()
        raw = graph_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        t1 = time.perf_counter()
        timings.append((t1 - t0) * 1000)

    best_ms = min(timings)
    assert best_ms < 250.0, f"Graph loading exceeded 250ms benchmark: {best_ms:.2f}ms"
    assert len(data.get("nodes", [])) == 6152
