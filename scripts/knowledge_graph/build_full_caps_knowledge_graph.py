"""
scripts/knowledge_graph/build_full_caps_knowledge_graph.py
===========================================================
Builds and serializes the complete, source-grounded CAPS Knowledge Graph
for all 51 curriculum scopes as well as individual scope graph artifacts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.domain.knowledge_graph_caps import (
    DEFAULT_TOPIC_MAPS_DIR,
    build_caps_graph,
    build_whole_curriculum_caps_graph,
    file_sha256,
)


def build_and_save_all(
    topic_maps_dir: Path = DEFAULT_TOPIC_MAPS_DIR,
    output_dir: Path | None = None,
    write_scopes: bool = True,
) -> dict[str, Any]:
    if output_dir is None:
        output_dir = REPO_ROOT / "data/knowledge_graph/caps_graph_foundation"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Building Whole CAPS Curriculum Knowledge Graph across all 51 scopes...")
    full_graph = build_whole_curriculum_caps_graph(topic_maps_dir)

    # 1. Save full curriculum graph
    full_graph_path = output_dir / "all_caps_curriculum_graph.json"
    full_graph_path.write_text(json.dumps(full_graph, indent=2) + "\n", encoding="utf-8")
    full_graph_sha = file_sha256(full_graph_path)

    # 2. Save full curriculum graph summary
    summary = {
        "graph_id": full_graph["graph_id"],
        "graph_version": full_graph["graph_version"],
        "status": full_graph["status"],
        "output": str(full_graph_path.relative_to(REPO_ROOT)),
        "source_sha256": full_graph["source"]["source_sha256"],
        "artifact_sha256": full_graph_sha,
        "valid": True,
        "counts": full_graph["counts"],
        "validation": {
            "valid": True,
            "node_count": full_graph["counts"]["nodes"],
            "edge_count": full_graph["counts"]["edges"],
            "counts": full_graph["counts"],
        },
    }
    summary_path = output_dir / "all_caps_curriculum_graph_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # 3. Save individual scope graphs
    scope_results: list[dict[str, Any]] = []
    if write_scopes:
        scopes_dir = output_dir / "scopes"
        scopes_dir.mkdir(parents=True, exist_ok=True)
        files = sorted(list(topic_maps_dir.glob("*.json")))

        for f in files:
            scope_graph = build_caps_graph(f)
            scope_name = f.stem
            if scope_name == "caps_topic_map_grade4_maths":
                scope_name = "grade4_mathematics_en"
            scope_file = scopes_dir / f"{scope_name}_caps_graph.json"
            scope_file.write_text(json.dumps(scope_graph, indent=2) + "\n", encoding="utf-8")
            scope_results.append({
                "scope_id": scope_name,
                "file": str(scope_file.relative_to(REPO_ROOT)),
                "nodes": scope_graph["counts"]["nodes"],
                "edges": scope_graph["counts"]["edges"],
                "topics": scope_graph["counts"]["topics"],
                "subtopics": scope_graph["counts"]["subtopics"],
            })

    result = {
        "full_graph_summary": summary,
        "individual_scopes_written": len(scope_results),
        "scopes": scope_results,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Full CAPS Curriculum Knowledge Graph Artifacts")
    parser.add_argument("--topic-maps-dir", default="data/caps/topic_maps",
                        help="Path to topic maps directory")
    parser.add_argument("--output-dir", default="data/knowledge_graph/caps_graph_foundation",
                        help="Output directory for knowledge graph artifacts")
    parser.add_argument("--no-scopes", action="store_true",
                        help="Do not generate individual scope graphs")
    parser.add_argument("--json", action="store_true", help="Print summary JSON to stdout")

    args = parser.parse_args()
    res = build_and_save_all(
        topic_maps_dir=REPO_ROOT / args.topic_maps_dir,
        output_dir=REPO_ROOT / args.output_dir,
        write_scopes=not args.no_scopes,
    )

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        counts = res["full_graph_summary"]["counts"]
        print("Whole CAPS Curriculum Graph Built Successfully!")
        print(f"  Nodes: {counts['nodes']}, Edges: {counts['edges']}")
        print(f"  Scopes: {counts['scopes']}, Terms: {counts['terms']}")
        print(f"  Topics: {counts['topics']}, Subtopics: {counts['subtopics']}")
        print(f"  Assessment Standards: {counts['assessment_statements']}")
        print(f"  Misconceptions: {counts['misconceptions']}")
        print(f"  Prerequisites: {counts['prerequisite_edges']}")
        print(f"  Output Artifact: {res['full_graph_summary']['output']}")
        print(f"  Individual Scopes Generated: {res['individual_scopes_written']}")


if __name__ == "__main__":
    main()
