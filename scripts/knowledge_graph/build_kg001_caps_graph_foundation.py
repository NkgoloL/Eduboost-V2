#!/usr/bin/env python3
"""Build the KG-1 Grade 4 Mathematics CAPS graph foundation artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.domain.knowledge_graph_caps import DEFAULT_SOURCE, build_caps_graph, validate_caps_graph

DEFAULT_OUTPUT = Path("data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph_summary.json")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    graph = build_caps_graph(Path(args.source))
    validation = validate_caps_graph(graph)
    result = {
        "valid": True,
        "graph_id": graph["graph_id"],
        "graph_version": graph["graph_version"],
        "source_sha256": graph["source"]["source_sha256"],
        "counts": graph["counts"],
        "validation": validation,
        "output": args.output,
    }
    if args.write:
        write_json(Path(args.output), graph)
        write_json(Path(args.summary), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"KG-1 CAPS graph valid: {result['valid']} nodes={graph['counts']['nodes']} edges={graph['counts']['edges']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
