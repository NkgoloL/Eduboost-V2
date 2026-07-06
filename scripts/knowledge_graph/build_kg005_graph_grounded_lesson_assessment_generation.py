#!/usr/bin/env python3
"""Build the KG-5 graph-grounded lesson and assessment generation artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_grounded_generation import (
    DEFAULT_GAP_PLAN,
    DEFAULT_TARGET_GRAPH,
    build_graph_grounded_generation_pack,
    validate_graph_grounded_generation_pack,
)

DEFAULT_OUTPUT = Path("data/knowledge_graph/grounded_generation/grade4_mathematics_graph_grounded_generation_pack.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/grounded_generation/grade4_mathematics_graph_grounded_generation_pack_summary.json")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gap-plan", default=str(DEFAULT_GAP_PLAN))
    parser.add_argument("--target-graph", default=str(DEFAULT_TARGET_GRAPH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary-output", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pack = build_graph_grounded_generation_pack(Path(args.gap_plan), Path(args.target_graph))
    validation = validate_graph_grounded_generation_pack(pack)
    summary = {
        "valid": validation["valid"],
        "graph_id": pack["graph_id"],
        "graph_version": pack["graph_version"],
        "counts": pack["counts"],
        "validation": validation,
        "output": args.output,
    }
    if args.write:
        write_json(Path(args.output), pack)
        write_json(Path(args.summary_output), summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "valid={} lesson_drafts={} assessment_drafts={}".format(
                str(validation["valid"]).lower(),
                pack["counts"]["lesson_drafts"],
                pack["counts"]["assessment_drafts"],
            )
        )
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
