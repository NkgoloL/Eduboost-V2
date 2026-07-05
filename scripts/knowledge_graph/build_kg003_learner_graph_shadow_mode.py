#!/usr/bin/env python3
"""Build the KG-3 learner graph shadow-mode artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_learner_shadow import (
    DEFAULT_OBSERVATIONS,
    DEFAULT_TARGET_GRAPH,
    build_learner_shadow_graph,
    validate_learner_shadow_graph,
)

DEFAULT_OUTPUT = Path("data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph_summary.json")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-graph", default=str(DEFAULT_TARGET_GRAPH))
    parser.add_argument("--observation-fixture", default=str(DEFAULT_OBSERVATIONS))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary-output", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    graph = build_learner_shadow_graph(Path(args.target_graph), Path(args.observation_fixture))
    validation = validate_learner_shadow_graph(graph)
    summary = {
        "valid": validation["valid"],
        "graph_id": graph["graph_id"],
        "graph_version": graph["graph_version"],
        "counts": graph["counts"],
        "validation": validation,
        "output": args.output,
    }
    if args.write:
        write_json(Path(args.output), graph)
        write_json(Path(args.summary_output), summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"valid={str(validation['valid']).lower()} learner_shadow_states={graph['counts']['learner_shadow_states']}")
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
