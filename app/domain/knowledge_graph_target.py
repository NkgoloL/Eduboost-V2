"""Pure target graph read-model helpers for KG-2.

KG-2 derives the expected Grade 4 Mathematics learner state from the approved
KG-1 CAPS graph artifact. This module intentionally has no database dependency
and does not update learner state. Runtime KG authority, learner graph state,
DB migrations, and learner-facing model changes remain out of scope.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_caps import validate_caps_graph

KG2_GRAPH_ID = "KG-2-TARGET-GRAPH-GRADE-4-MATHEMATICS"
KG2_GRAPH_VERSION = "kg2-target-graph-v1"
DEFAULT_CAPS_GRAPH = Path("data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json")

TARGET_NODE_TYPES = {"topic", "subtopic", "assessment_statement"}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(prefix: str, key: str) -> str:
    return f"{prefix}_{sha256_text(key)[:24]}"


@dataclass(frozen=True)
class TargetState:
    target_id: str
    target_key: str
    target_type: str
    caps_node_key: str
    caps_node_id: str
    label: str
    grade: int
    subject: str
    term: int
    required_mastery: float
    required_confidence: float
    priority: float
    pacing_window: str
    source_ref: str
    source_sha256: str
    caps_source_ref: str
    caps_source_sha256: str
    review_status: str = "approved"
    version: str = KG2_GRAPH_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_key": self.target_key,
            "target_type": self.target_type,
            "caps_node_key": self.caps_node_key,
            "caps_node_id": self.caps_node_id,
            "label": self.label,
            "grade": self.grade,
            "subject": self.subject,
            "term": self.term,
            "required_mastery": self.required_mastery,
            "required_confidence": self.required_confidence,
            "priority": self.priority,
            "pacing_window": self.pacing_window,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "caps_source_ref": self.caps_source_ref,
            "caps_source_sha256": self.caps_source_sha256,
            "review_status": self.review_status,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TargetEdge:
    target_edge_id: str
    source_target_key: str
    target_target_key: str
    edge_type: str
    label: str
    source_ref: str
    source_sha256: str
    review_status: str = "approved"
    version: str = KG2_GRAPH_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_edge_id": self.target_edge_id,
            "source_target_key": self.source_target_key,
            "target_target_key": self.target_target_key,
            "edge_type": self.edge_type,
            "label": self.label,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "review_status": self.review_status,
            "version": self.version,
            "metadata": self.metadata,
        }


def _target_key(caps_node_key: str) -> str:
    return f"target:g4m:{caps_node_key}"


def _thresholds(node_type: str, term: int) -> tuple[float, float, float]:
    """Return required mastery, confidence and priority for a node type/term."""
    term_weight = {1: 1.00, 2: 0.95, 3: 0.90, 4: 0.85}.get(term, 0.80)
    if node_type == "topic":
        return 0.75, 0.70, round(0.70 * term_weight, 3)
    if node_type == "subtopic":
        return 0.80, 0.75, round(0.85 * term_weight, 3)
    return 0.85, 0.80, round(1.00 * term_weight, 3)


def _pacing_window(term: int) -> str:
    windows = {
        1: "term-1-weeks-1-10",
        2: "term-2-weeks-11-20",
        3: "term-3-weeks-21-30",
        4: "term-4-weeks-31-40",
    }
    return windows.get(term, "grade-4-window-unspecified")


def build_target_graph(caps_graph_path: Path = DEFAULT_CAPS_GRAPH) -> dict[str, Any]:
    caps_graph_path = Path(caps_graph_path)
    caps_graph = json.loads(caps_graph_path.read_text(encoding="utf-8"))
    validate_caps_graph(caps_graph)
    caps_graph_hash = file_sha256(caps_graph_path)
    scope = caps_graph.get("scope", {})
    grade = int(scope.get("grade") or 4)
    subject = str(scope.get("subject") or "mathematics")

    caps_nodes = {node["node_key"]: node for node in caps_graph.get("nodes", [])}
    target_states: dict[str, TargetState] = {}
    target_edges: dict[str, TargetEdge] = {}

    for node in caps_graph.get("nodes", []):
        node_type = node.get("node_type")
        if node_type not in TARGET_NODE_TYPES:
            continue
        if node.get("review_status") != "approved":
            continue
        if int(node.get("grade") or 0) != grade or str(node.get("subject") or "") != subject:
            continue
        term = int(node.get("term") or 0)
        mastery, confidence, priority = _thresholds(node_type, term)
        caps_node_key = node["node_key"]
        target_key = _target_key(caps_node_key)
        state = TargetState(
            target_id=stable_id("kgt", target_key),
            target_key=target_key,
            target_type=node_type,
            caps_node_key=caps_node_key,
            caps_node_id=node["node_id"],
            label=node["label"],
            grade=grade,
            subject=subject,
            term=term,
            required_mastery=mastery,
            required_confidence=confidence,
            priority=priority,
            pacing_window=_pacing_window(term),
            source_ref=f"KG-1:{caps_node_key}",
            source_sha256=caps_graph_hash,
            caps_source_ref=node.get("source_ref", ""),
            caps_source_sha256=node.get("source_sha256", ""),
            metadata={
                "caps_node_type": node_type,
                "caps_graph_id": caps_graph.get("graph_id"),
                "caps_graph_version": caps_graph.get("graph_version"),
                "target_policy": "kg2-default-grade-4-mathematics",
            },
        )
        target_states[target_key] = state

    def add_edge(source_caps_key: str, target_caps_key: str, edge_type: str, label: str, caps_edge: dict[str, Any]) -> None:
        source_key = _target_key(source_caps_key)
        target_key = _target_key(target_caps_key)
        if source_key not in target_states or target_key not in target_states:
            return
        raw_key = f"{source_key}|{edge_type}|{target_key}"
        edge = TargetEdge(
            target_edge_id=stable_id("kgte", raw_key),
            source_target_key=source_key,
            target_target_key=target_key,
            edge_type=edge_type,
            label=label,
            source_ref=f"KG-1-edge:{caps_edge.get('edge_id', raw_key)}",
            source_sha256=caps_graph_hash,
            metadata={
                "caps_edge_type": caps_edge.get("edge_type"),
                "caps_source_node_key": source_caps_key,
                "caps_target_node_key": target_caps_key,
            },
        )
        target_edges[edge.target_edge_id] = edge

    for edge in caps_graph.get("edges", []):
        caps_edge_type = edge.get("edge_type")
        source = edge.get("source_node_key")
        target = edge.get("target_node_key")
        if not source or not target:
            continue
        if caps_edge_type == "contains":
            source_type = caps_nodes.get(source, {}).get("node_type")
            target_type = caps_nodes.get(target, {}).get("node_type")
            if source_type in TARGET_NODE_TYPES and target_type in TARGET_NODE_TYPES:
                add_edge(source, target, "target_contains", "Target parent contains target child", edge)
        elif caps_edge_type == "assesses":
            add_edge(source, target, "target_assesses", "Target subtopic assessed by target statement", edge)
        elif caps_edge_type == "prerequisite_of":
            add_edge(source, target, "target_prerequisite_of", "Target prerequisite relationship", edge)

    states = [state.as_dict() for state in sorted(target_states.values(), key=lambda s: s.target_key)]
    edges = [edge.as_dict() for edge in sorted(target_edges.values(), key=lambda e: (e.source_target_key, e.edge_type, e.target_target_key))]
    counts = {
        "target_states": len(states),
        "topic_targets": sum(1 for s in states if s["target_type"] == "topic"),
        "subtopic_targets": sum(1 for s in states if s["target_type"] == "subtopic"),
        "assessment_statement_targets": sum(1 for s in states if s["target_type"] == "assessment_statement"),
        "target_edges": len(edges),
        "target_prerequisite_edges": sum(1 for e in edges if e["edge_type"] == "target_prerequisite_of"),
    }

    graph = {
        "graph_id": KG2_GRAPH_ID,
        "graph_version": KG2_GRAPH_VERSION,
        "status": "target_graph_generated",
        "scope": {"curriculum": "CAPS", "grade": grade, "subject": subject, "language": "en", "beta_scope": "Grade 4 Mathematics"},
        "source": {
            "caps_graph_path": str(caps_graph_path),
            "caps_graph_sha256": caps_graph_hash,
            "caps_graph_id": caps_graph.get("graph_id"),
            "caps_graph_version": caps_graph.get("graph_version"),
            "caps_source_sha256": caps_graph.get("source", {}).get("source_sha256"),
        },
        "policies": {
            "policy_id": "kg2-default-grade-4-mathematics",
            "required_mastery_thresholds_present": True,
            "required_confidence_thresholds_present": True,
            "priority_weighting_present": True,
            "pacing_windows_present": True,
            "target_types": sorted(TARGET_NODE_TYPES),
        },
        "review": {"target_review_status": "approved", "runtime_authority": "target_graph_read_model_only"},
        "counts": counts,
        "target_states": states,
        "target_edges": edges,
        "boundary": {
            "runtime_kg_implementation_claimed": False,
            "runtime_kg_authority_switch_authorised": False,
            "database_schema_migration_authorised": False,
            "learner_facing_model_change_authorised": False,
            "learner_graph_implementation_authorised": False,
            "target_graph_runtime_authority_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
        },
    }
    validate_target_graph(graph, caps_graph)
    return graph


def validate_target_graph(target_graph: dict[str, Any], caps_graph: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    states = target_graph.get("target_states", [])
    edges = target_graph.get("target_edges", [])
    state_keys = [state.get("target_key") for state in states]
    state_key_set = set(state_keys)
    caps_nodes = {node["node_key"]: node for node in (caps_graph or {}).get("nodes", [])}

    if target_graph.get("graph_id") != KG2_GRAPH_ID:
        errors.append("target graph id must be KG-2 target graph id")
    if target_graph.get("scope", {}).get("grade") != 4:
        errors.append("target graph must be scoped to Grade 4")
    if target_graph.get("scope", {}).get("subject") != "mathematics":
        errors.append("target graph must be scoped to Mathematics")
    if len(state_key_set) != len(state_keys):
        errors.append("duplicate target keys found")
    if len(states) < 100:
        errors.append("target graph must contain at least 100 target states")
    if target_graph.get("counts", {}).get("target_prerequisite_edges", 0) < 20:
        errors.append("target graph must preserve prerequisite target edges")

    for state in states:
        if state.get("review_status") != "approved":
            errors.append(f"target state must be approved: {state.get('target_key')}")
        if int(state.get("grade") or 0) != 4 or state.get("subject") != "mathematics":
            errors.append(f"target state outside Grade 4 Mathematics scope: {state.get('target_key')}")
        if not state.get("caps_node_key") or not state.get("caps_node_id"):
            errors.append(f"target state missing CAPS reference: {state.get('target_key')}")
        if caps_nodes and state.get("caps_node_key") not in caps_nodes:
            errors.append(f"target state references missing CAPS node: {state.get('target_key')}")
        if not state.get("source_ref") or not state.get("source_sha256"):
            errors.append(f"target state missing KG-1 provenance: {state.get('target_key')}")
        if not state.get("caps_source_ref") or not state.get("caps_source_sha256"):
            errors.append(f"target state missing CAPS source provenance: {state.get('target_key')}")
        for key in ("required_mastery", "required_confidence", "priority"):
            value = state.get(key)
            if not isinstance(value, (int, float)) or value <= 0 or value > 1:
                errors.append(f"target state has invalid {key}: {state.get('target_key')}")
        if not state.get("pacing_window"):
            errors.append(f"target state missing pacing window: {state.get('target_key')}")

    for edge in edges:
        if edge.get("review_status") != "approved":
            errors.append(f"target edge must be approved: {edge.get('target_edge_id')}")
        if edge.get("source_target_key") not in state_key_set or edge.get("target_target_key") not in state_key_set:
            errors.append(f"target edge has orphan endpoint: {edge.get('target_edge_id')}")
        if not edge.get("source_ref") or not edge.get("source_sha256"):
            errors.append(f"target edge missing provenance: {edge.get('target_edge_id')}")

    for key, value in target_graph.get("boundary", {}).items():
        if value is not False:
            errors.append(f"boundary flag must be false: {key}")
    if errors:
        raise ValueError("; ".join(errors))
    return {"valid": True, "target_state_count": len(states), "target_edge_count": len(edges), "counts": target_graph.get("counts", {})}
