#!/usr/bin/env python3
"""Build the KG-4 advisory gap-engine and intervention-planner artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_gap_engine import (
    DEFAULT_SHADOW_GRAPH,
    DEFAULT_TARGET_GRAPH,
    build_gap_intervention_plan,
    validate_gap_intervention_plan,
)

DEFAULT_OUTPUT = Path("data/knowledge_graph/gap_engine/grade4_mathematics_gap_intervention_plan.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/gap_engine/grade4_mathematics_gap_intervention_plan_summary.json")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shadow-graph", default=str(DEFAULT_SHADOW_GRAPH))
    parser.add_argument("--target-graph", default=str(DEFAULT_TARGET_GRAPH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary-output", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    plan = build_gap_intervention_plan(Path(args.shadow_graph), Path(args.target_graph))
    validation = validate_gap_intervention_plan(plan)
    summary = {
        "valid": validation["valid"],
        "graph_id": plan["graph_id"],
        "graph_version": plan["graph_version"],
        "counts": plan["counts"],
        "validation": validation,
        "output": args.output,
    }
    if args.write:
        write_json(Path(args.output), plan)
        write_json(Path(args.summary_output), summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"valid={str(validation['valid']).lower()} gap_items={plan['counts']['gap_items']} interventions={plan['counts']['intervention_recommendations']}")
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
