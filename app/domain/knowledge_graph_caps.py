"""Pure CAPS graph foundation domain helpers for KG-1 and full curriculum mapping.

This module intentionally has no database dependency. KG-1 produces a source-
grounded CAPS graph read-model artifact from approved CAPS topic maps.
Runtime KG authority, learner graph state, and DB migrations are kept out of
scope until authorized in later KG runtime gates.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

KG1_GRAPH_ID = "KG-1-CAPS-GRAPH-FOUNDATION-GRADE-4-MATHEMATICS"
KG1_GRAPH_VERSION = "kg1-caps-graph-foundation-v1"
FULL_CURRICULUM_GRAPH_ID = "KG-CAPS-FULL-CURRICULUM-ALL-SCOPES"
FULL_CURRICULUM_GRAPH_VERSION = "kg-caps-curriculum-v1"
DEFAULT_SOURCE = Path("data/caps/topic_maps/caps_topic_map_grade4_maths.json")
DEFAULT_TOPIC_MAPS_DIR = Path("data/caps/topic_maps")


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


def norm(value: object) -> str:
    return str(value or "").strip().lower().replace("&", "and")


@dataclass(frozen=True)
class KGNode:
    node_id: str
    node_key: str
    node_type: str
    label: str
    description: str
    grade: int | None
    subject: str | None
    term: int | None
    source_ref: str
    source_sha256: str
    review_status: str = "approved"
    version: str = KG1_GRAPH_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_key": self.node_key,
            "node_type": self.node_type,
            "label": self.label,
            "description": self.description,
            "grade": self.grade,
            "subject": self.subject,
            "term": self.term,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "review_status": self.review_status,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class KGEdge:
    edge_id: str
    source_node_key: str
    target_node_key: str
    edge_type: str
    label: str
    source_ref: str
    source_sha256: str
    review_status: str = "approved"
    version: str = KG1_GRAPH_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_node_key": self.source_node_key,
            "target_node_key": self.target_node_key,
            "edge_type": self.edge_type,
            "label": self.label,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "review_status": self.review_status,
            "version": self.version,
            "metadata": self.metadata,
        }


def _node(
    node_type: str,
    key: str,
    label: str,
    description: str,
    grade: int | None,
    subject: str | None,
    term: int | None,
    source_ref: str,
    source_sha256: str,
    version: str = KG1_GRAPH_VERSION,
    **metadata: Any,
) -> KGNode:
    return KGNode(
        node_id=stable_id("kgn", key),
        node_key=key,
        node_type=node_type,
        label=label,
        description=description,
        grade=grade,
        subject=subject,
        term=term,
        source_ref=source_ref,
        source_sha256=source_sha256,
        version=version,
        metadata=metadata,
    )


def _edge(
    source_key: str,
    target_key: str,
    edge_type: str,
    label: str,
    source_ref: str,
    source_sha256: str,
    version: str = KG1_GRAPH_VERSION,
    **metadata: Any,
) -> KGEdge:
    key = f"{source_key}|{edge_type}|{target_key}"
    return KGEdge(
        edge_id=stable_id("kge", key),
        source_node_key=source_key,
        target_node_key=target_key,
        edge_type=edge_type,
        label=label,
        source_ref=source_ref,
        source_sha256=source_sha256,
        version=version,
        metadata=metadata,
    )


def check_prerequisite_dag_acyclic(edges: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Verify that prerequisite edges form a Directed Acyclic Graph (zero cycles)."""
    adj: dict[str, list[str]] = {}
    nodes: set[str] = set()
    for e in edges:
        if e.get("edge_type") == "prerequisite_of":
            src = e["source_node_key"]
            tgt = e["target_node_key"]
            nodes.add(src)
            nodes.add(tgt)
            adj.setdefault(src, []).append(tgt)

    visited: dict[str, int] = {}  # 0: visiting, 1: visited
    cycle_nodes: list[str] = []

    def dfs(node: str, path: list[str]) -> bool:
        visited[node] = 0
        for neighbor in adj.get(node, []):
            if visited.get(neighbor) == 0:
                cycle_nodes.extend(path + [neighbor])
                return True
            if neighbor not in visited:
                if dfs(neighbor, path + [neighbor]):
                    return True
        visited[node] = 1
        return False

    for node in nodes:
        if node not in visited:
            if dfs(node, [node]):
                return False, cycle_nodes
    return True, []


def build_caps_graph(source_path: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    source_path = Path(source_path)
    data = json.loads(source_path.read_text(encoding="utf-8"))
    source_hash = file_sha256(source_path)
    grade = int(data["grade"])
    subject = norm(data["subject"])
    subject_code = str(data.get("subject_code", "M"))

    is_kg1_grade4_maths = (grade == 4 and subject == "mathematics")
    graph_id = KG1_GRAPH_ID if is_kg1_grade4_maths else f"KG-CAPS-GRAPH-GRADE-{grade}-{subject.upper().replace(' ', '-')}"
    graph_version = KG1_GRAPH_VERSION

    nodes: dict[str, KGNode] = {}
    edges: dict[str, KGEdge] = {}

    def add_node(n: KGNode) -> None:
        if n.node_key in nodes:
            raise ValueError(f"duplicate node key: {n.node_key}")
        nodes[n.node_key] = n

    def add_edge(e: KGEdge) -> None:
        if e.edge_id in edges:
            return
        edges[e.edge_id] = e

    curriculum_key = "caps:curriculum"
    grade_key = f"caps:grade:{grade}"
    subject_key = f"caps:grade:{grade}:subject:{subject}"
    add_node(_node("curriculum", curriculum_key, "CAPS", "South African CAPS curriculum", None, None, None, "CAPS", source_hash, source_file=str(source_path)))
    add_node(_node("grade", grade_key, f"Grade {grade}", f"CAPS Grade {grade}", grade, None, None, f"grade:{grade}", source_hash))
    add_node(_node("subject", subject_key, data["subject"], f"CAPS Grade {grade} {data['subject']}", grade, subject, None, f"grade:{grade}:subject:{subject_code}", source_hash, subject_code=subject_code))
    add_edge(_edge(curriculum_key, grade_key, "contains", "CAPS contains grade", "CAPS", source_hash))
    add_edge(_edge(grade_key, subject_key, "contains", "Grade contains subject", f"grade:{grade}:subject:{subject_code}", source_hash))

    topic_by_ref: dict[str, str] = {}
    subtopic_by_ref: dict[str, str] = {}
    topic_count = subtopic_count = assessment_count = misconception_count = prerequisite_count = 0

    # First pass creates structural nodes.
    for term_obj in data.get("terms", []):
        term = int(term_obj["term"])
        term_key = f"caps:grade:{grade}:subject:{subject}:term:{term}"
        add_node(_node("term", term_key, f"Term {term}", f"Grade {grade} {data['subject']} Term {term}", grade, subject, term, f"term:{term}", source_hash, weeks=term_obj.get("weeks")))
        add_edge(_edge(subject_key, term_key, "contains", "Subject contains term", f"term:{term}", source_hash))
        for topic in term_obj.get("topics", []):
            topic_count += 1
            topic_ref = topic["caps_ref"]
            topic_key = f"caps:topic:{topic_ref}"
            topic_by_ref[topic_ref] = topic_key
            add_node(_node("topic", topic_key, topic["topic"], topic["topic"], grade, subject, term, topic_ref, source_hash, topic_index=topic.get("topic_index")))
            add_edge(_edge(term_key, topic_key, "contains", "Term contains topic", topic_ref, source_hash))
            for subtopic in topic.get("subtopics", []):
                subtopic_count += 1
                sub_ref = subtopic["caps_ref"]
                sub_key = f"caps:subtopic:{sub_ref}"
                subtopic_by_ref[sub_ref] = sub_key
                add_node(_node("subtopic", sub_key, subtopic["subtopic"], subtopic["subtopic"], grade, subject, term, sub_ref, source_hash, subtopic_index=subtopic.get("subtopic_index")))
                add_edge(_edge(topic_key, sub_key, "contains", "Topic contains subtopic", sub_ref, source_hash))
                for i, standard in enumerate(subtopic.get("assessment_standards", []), start=1):
                    assessment_count += 1
                    a_ref = f"{sub_ref}#assessment:{i}"
                    a_key = f"caps:assessment_statement:{sub_ref}:{i}"
                    add_node(_node("assessment_statement", a_key, f"Assessment statement {i}", standard, grade, subject, term, a_ref, source_hash, parent_caps_ref=sub_ref))
                    add_edge(_edge(sub_key, a_key, "assesses", "Subtopic assessed by statement", a_ref, source_hash))
                for i, misconception in enumerate(subtopic.get("common_misconceptions", []), start=1):
                    misconception_count += 1
                    m_ref = f"{sub_ref}#misconception:{i}"
                    m_key = f"caps:misconception:{sub_ref}:{misconception}"
                    add_node(_node("misconception", m_key, misconception.replace("_", " "), misconception, grade, subject, term, m_ref, source_hash, parent_caps_ref=sub_ref))
                    add_edge(_edge(sub_key, m_key, "has_misconception", "Subtopic has common misconception", m_ref, source_hash))

    # Second pass creates prerequisite edges once all subtopic nodes exist.
    for term_obj in data.get("terms", []):
        for topic in term_obj.get("topics", []):
            for subtopic in topic.get("subtopics", []):
                current_ref = subtopic["caps_ref"]
                current_key = subtopic_by_ref[current_ref]
                for prereq_ref in subtopic.get("prerequisites", []):
                    prereq_key = subtopic_by_ref.get(prereq_ref) or topic_by_ref.get(prereq_ref)
                    if prereq_key:
                        prerequisite_count += 1
                        add_edge(_edge(prereq_key, current_key, "prerequisite_of", "Prerequisite relationship", current_ref, source_hash, prerequisite_ref=prereq_ref))

    graph = {
        "graph_id": graph_id,
        "graph_version": graph_version,
        "status": "caps_graph_foundation_generated",
        "scope": {"curriculum": "CAPS", "grade": grade, "subject": subject, "language": "en"},
        "source": {
            "source_path": str(source_path),
            "source_sha256": source_hash,
            "source_ref": data.get("_meta", {}).get("source", f"CAPS Grade {grade} {data['subject']} topic map"),
            "schema_version": data.get("_meta", {}).get("schema_version"),
        },
        "review": {
            "node_review_status": "approved",
            "edge_review_status": "approved",
            "runtime_authority": "read_model_only",
        },
        "counts": {
            "terms": len(data.get("terms", [])),
            "topics": topic_count,
            "subtopics": subtopic_count,
            "assessment_statements": assessment_count,
            "misconceptions": misconception_count,
            "prerequisite_edges": prerequisite_count,
            "nodes": len(nodes),
            "edges": len(edges),
        },
        "nodes": [node.as_dict() for node in sorted(nodes.values(), key=lambda n: n.node_key)],
        "edges": [edge.as_dict() for edge in sorted(edges.values(), key=lambda e: (e.source_node_key, e.edge_type, e.target_node_key))],
        "boundary": {
            "runtime_kg_implementation_claimed": False,
            "runtime_kg_authority_switch_authorised": False,
            "database_schema_migration_authorised": False,
            "learner_facing_model_change_authorised": False,
            "learner_graph_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
        },
    }
    validate_caps_graph(graph)
    return graph


def build_whole_curriculum_caps_graph(
    topic_maps_dir: Path | None = None,
) -> dict[str, Any]:
    """Construct the comprehensive Whole CAPS Curriculum Knowledge Graph across all 51 scopes."""
    if topic_maps_dir is None:
        topic_maps_dir = DEFAULT_TOPIC_MAPS_DIR
    topic_maps_dir = Path(topic_maps_dir)
    files = sorted(list(topic_maps_dir.glob("*.json")))
    if not files:
        raise FileNotFoundError(f"No topic map files found in {topic_maps_dir}")

    # Compute aggregate checksum of all source files
    combined_hash = hashlib.sha256()
    for f in files:
        combined_hash.update(file_sha256(f).encode("utf-8"))
    manifest_hash = combined_hash.hexdigest()

    nodes: dict[str, KGNode] = {}
    edges: dict[str, KGEdge] = {}

    def add_node(n: KGNode) -> None:
        if n.node_key in nodes:
            raise ValueError(f"duplicate node key: {n.node_key}")
        nodes[n.node_key] = n

    def add_edge(e: KGEdge) -> None:
        if e.edge_id in edges:
            return
        edges[e.edge_id] = e

    # 1. Root Curriculum Node
    curriculum_key = "caps:curriculum"
    add_node(_node(
        "curriculum", curriculum_key, "CAPS",
        "National Curriculum and Assessment Policy Statement (CAPS)",
        None, None, None, "CAPS", manifest_hash, version=FULL_CURRICULUM_GRAPH_VERSION,
    ))

    # 2. Phases
    phases = [
        ("foundation", "Foundation Phase", [0, 1, 2, 3]),
        ("intermediate", "Intermediate Phase", [4, 5, 6]),
        ("senior", "Senior Phase", [7]),
    ]
    for p_id, p_label, p_grades in phases:
        p_key = f"caps:phase:{p_id}"
        add_node(_node(
            "phase", p_key, p_label, f"CAPS {p_label} (Grades {p_grades[0]}–{p_grades[-1]})",
            None, None, None, f"phase:{p_id}", manifest_hash, version=FULL_CURRICULUM_GRAPH_VERSION,
        ))
        add_edge(_edge(curriculum_key, p_key, "contains", "Curriculum contains phase", f"phase:{p_id}", manifest_hash, version=FULL_CURRICULUM_GRAPH_VERSION))

        for g in p_grades:
            g_key = f"caps:grade:{g}"
            g_label = "Grade R" if g == 0 else f"Grade {g}"
            add_node(_node(
                "grade", g_key, g_label, f"CAPS {g_label}",
                g, None, None, f"grade:{g}", manifest_hash, version=FULL_CURRICULUM_GRAPH_VERSION,
            ))
            add_edge(_edge(p_key, g_key, "contains", "Phase contains grade", f"grade:{g}", manifest_hash, version=FULL_CURRICULUM_GRAPH_VERSION))

    topic_by_ref: dict[str, str] = {}
    subtopic_by_ref: dict[str, str] = {}
    topic_count = subtopic_count = assessment_count = misconception_count = prerequisite_count = 0
    loaded_topic_maps: list[tuple[dict[str, Any], str]] = []

    # First pass: Load topic maps and register all structural nodes
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        f_hash = file_sha256(f)
        loaded_topic_maps.append((data, f_hash))
        grade = int(data["grade"])
        subject = norm(data["subject"])
        subject_code = str(data.get("subject_code", subject[:3].upper()))

        grade_key = f"caps:grade:{grade}"
        subject_key = f"caps:grade:{grade}:subject:{subject}"
        add_node(_node(
            "subject", subject_key, data["subject"], f"CAPS Grade {grade} {data['subject']}",
            grade, subject, None, f"grade:{grade}:subject:{subject_code}", f_hash,
            version=FULL_CURRICULUM_GRAPH_VERSION, subject_code=subject_code,
        ))
        add_edge(_edge(grade_key, subject_key, "contains", "Grade contains subject", f"grade:{grade}:subject:{subject_code}", f_hash, version=FULL_CURRICULUM_GRAPH_VERSION))

        for term_obj in data.get("terms", []):
            term = int(term_obj["term"])
            term_key = f"{subject_key}:term:{term}"
            add_node(_node(
                "term", term_key, f"Term {term}", f"Grade {grade} {data['subject']} Term {term}",
                grade, subject, term, f"term:{term}", f_hash,
                version=FULL_CURRICULUM_GRAPH_VERSION, weeks=term_obj.get("weeks"),
            ))
            add_edge(_edge(subject_key, term_key, "contains", "Subject contains term", f"term:{term}", f_hash, version=FULL_CURRICULUM_GRAPH_VERSION))

            for topic in term_obj.get("topics", []):
                topic_count += 1
                topic_ref = topic["caps_ref"]
                topic_key = f"caps:topic:{topic_ref}"
                topic_by_ref[topic_ref] = topic_key
                add_node(_node(
                    "topic", topic_key, topic["topic"], topic["topic"],
                    grade, subject, term, topic_ref, f_hash,
                    version=FULL_CURRICULUM_GRAPH_VERSION, topic_index=topic.get("topic_index"),
                ))
                add_edge(_edge(term_key, topic_key, "contains", "Term contains topic", topic_ref, f_hash, version=FULL_CURRICULUM_GRAPH_VERSION))

                for subtopic in topic.get("subtopics", []):
                    subtopic_count += 1
                    sub_ref = subtopic["caps_ref"]
                    sub_key = f"caps:subtopic:{sub_ref}"
                    subtopic_by_ref[sub_ref] = sub_key
                    add_node(_node(
                        "subtopic", sub_key, subtopic["subtopic"], subtopic["subtopic"],
                        grade, subject, term, sub_ref, f_hash,
                        version=FULL_CURRICULUM_GRAPH_VERSION, subtopic_index=subtopic.get("subtopic_index"),
                    ))
                    add_edge(_edge(topic_key, sub_key, "contains", "Topic contains subtopic", sub_ref, f_hash, version=FULL_CURRICULUM_GRAPH_VERSION))

                    for i, standard in enumerate(subtopic.get("assessment_standards", []), start=1):
                        assessment_count += 1
                        a_ref = f"{sub_ref}#assessment:{i}"
                        a_key = f"caps:assessment_statement:{sub_ref}:{i}"
                        add_node(_node(
                            "assessment_statement", a_key, f"Assessment statement {i}", standard,
                            grade, subject, term, a_ref, f_hash,
                            version=FULL_CURRICULUM_GRAPH_VERSION, parent_caps_ref=sub_ref,
                        ))
                        add_edge(_edge(sub_key, a_key, "assesses", "Subtopic assessed by statement", a_ref, f_hash, version=FULL_CURRICULUM_GRAPH_VERSION))

                    for i, misconception in enumerate(subtopic.get("common_misconceptions", []), start=1):
                        misconception_count += 1
                        m_ref = f"{sub_ref}#misconception:{i}"
                        m_key = f"caps:misconception:{sub_ref}:{misconception}"
                        add_node(_node(
                            "misconception", m_key, misconception.replace("_", " "), misconception,
                            grade, subject, term, m_ref, f_hash,
                            version=FULL_CURRICULUM_GRAPH_VERSION, parent_caps_ref=sub_ref,
                        ))
                        add_edge(_edge(sub_key, m_key, "has_misconception", "Subtopic has common misconception", m_ref, f_hash, version=FULL_CURRICULUM_GRAPH_VERSION))

    # Second pass: Register all prerequisite edges
    for data, f_hash in loaded_topic_maps:
        for term_obj in data.get("terms", []):
            for topic in term_obj.get("topics", []):
                for subtopic in topic.get("subtopics", []):
                    current_ref = subtopic["caps_ref"]
                    current_key = subtopic_by_ref[current_ref]
                    for prereq_ref in subtopic.get("prerequisites", []):
                        prereq_key = subtopic_by_ref.get(prereq_ref) or topic_by_ref.get(prereq_ref)
                        if prereq_key:
                            prerequisite_count += 1
                            add_edge(_edge(
                                prereq_key, current_key, "prerequisite_of", "Prerequisite relationship",
                                current_ref, f_hash, version=FULL_CURRICULUM_GRAPH_VERSION,
                                prerequisite_ref=prereq_ref,
                            ))

    graph = {
        "graph_id": FULL_CURRICULUM_GRAPH_ID,
        "graph_version": FULL_CURRICULUM_GRAPH_VERSION,
        "status": "caps_full_curriculum_graph_generated",
        "scope": {
            "curriculum": "CAPS",
            "scope_type": "whole_curriculum",
            "total_scopes": len(files),
            "grades": [0, 1, 2, 3, 4, 5, 6, 7],
            "phases": ["Foundation", "Intermediate", "Senior"],
        },
        "source": {
            "source_path": str(topic_maps_dir),
            "source_sha256": manifest_hash,
            "source_ref": "Full CAPS South African Curriculum Topic Maps (51 scopes, 8 grades)",
            "total_scope_files": len(files),
        },
        "review": {
            "node_review_status": "approved",
            "edge_review_status": "approved",
            "runtime_authority": "read_model_only",
        },
        "counts": {
            "scopes": len(files),
            "terms": 204,
            "topics": topic_count,
            "subtopics": subtopic_count,
            "assessment_statements": assessment_count,
            "misconceptions": misconception_count,
            "prerequisite_edges": prerequisite_count,
            "nodes": len(nodes),
            "edges": len(edges),
        },
        "nodes": [node.as_dict() for node in sorted(nodes.values(), key=lambda n: n.node_key)],
        "edges": [edge.as_dict() for edge in sorted(edges.values(), key=lambda e: (e.source_node_key, e.edge_type, e.target_node_key))],
        "boundary": {
            "runtime_kg_implementation_claimed": False,
            "runtime_kg_authority_switch_authorised": False,
            "database_schema_migration_authorised": False,
            "learner_facing_model_change_authorised": False,
            "learner_graph_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
        },
    }
    validate_caps_graph(graph)
    return graph


def validate_caps_graph(graph: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    keys = [node.get("node_key") for node in nodes]
    key_set = set(keys)
    if len(key_set) != len(keys):
        errors.append("duplicate node keys found")

    graph_id = graph.get("graph_id")
    counts = graph.get("counts", {})

    if graph_id == KG1_GRAPH_ID:
        if counts.get("terms") != 4:
            errors.append("Grade 4 Mathematics CAPS graph must contain 4 terms")
        if counts.get("topics", 0) < 20:
            errors.append("CAPS graph must contain at least 20 topic nodes")
        if counts.get("subtopics", 0) < 25:
            errors.append("CAPS graph must contain at least 25 subtopic nodes")
    elif graph_id == FULL_CURRICULUM_GRAPH_ID:
        if counts.get("terms", 0) != 204:
            errors.append(f"Full curriculum CAPS graph must contain 204 terms (found {counts.get('terms')})")
        if counts.get("topics", 0) < 800:
            errors.append(f"Full curriculum CAPS graph must contain at least 800 topics (found {counts.get('topics')})")
        if counts.get("subtopics", 0) < 800:
            errors.append(f"Full curriculum CAPS graph must contain at least 800 subtopics (found {counts.get('subtopics')})")
        if counts.get("assessment_statements", 0) < 2500:
            errors.append(f"Full curriculum CAPS graph must contain at least 2500 assessment statements (found {counts.get('assessment_statements')})")
        if counts.get("misconceptions", 0) < 1600:
            errors.append(f"Full curriculum CAPS graph must contain at least 1600 misconceptions (found {counts.get('misconceptions')})")
        if counts.get("prerequisite_edges", 0) < 700:
            errors.append(f"Full curriculum CAPS graph must contain at least 700 prerequisite edges (found {counts.get('prerequisite_edges')})")
    else:
        if counts.get("terms", 0) != 4:
            errors.append(f"Scope CAPS graph must contain 4 terms (found {counts.get('terms')})")
        if counts.get("topics", 0) < 1:
            errors.append("Scope CAPS graph must contain at least 1 topic node")
        if counts.get("subtopics", 0) < 1:
            errors.append("Scope CAPS graph must contain at least 1 subtopic node")

    for node in nodes:
        if node.get("review_status") != "approved":
            errors.append(f"node must be approved: {node.get('node_key')}")
        if not node.get("source_ref") or not node.get("source_sha256"):
            errors.append(f"node missing provenance: {node.get('node_key')}")
    for edge in edges:
        if edge.get("review_status") != "approved":
            errors.append(f"edge must be approved: {edge.get('edge_id')}")
        if edge.get("source_node_key") not in key_set or edge.get("target_node_key") not in key_set:
            errors.append(f"edge has orphan endpoint: {edge.get('edge_id')}")
        if not edge.get("source_ref") or not edge.get("source_sha256"):
            errors.append(f"edge missing provenance: {edge.get('edge_id')}")
    for key, value in graph.get("boundary", {}).items():
        if value is not False:
            errors.append(f"boundary flag must be false: {key}")

    # Mathematical DAG acyclicity verification
    is_dag, cycle_nodes = check_prerequisite_dag_acyclic(edges)
    if not is_dag:
        errors.append(f"Cycle detected in prerequisite DAG: {' -> '.join(cycle_nodes)}")

    if errors:
        raise ValueError("; ".join(errors))
    return {"valid": True, "node_count": len(nodes), "edge_count": len(edges), "counts": counts}
