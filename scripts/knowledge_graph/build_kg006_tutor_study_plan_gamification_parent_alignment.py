#!/usr/bin/env python3
"""Build the KG-6 tutor/study-plan/gamification/parent alignment artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_product_alignment import (
    DEFAULT_GENERATION_PACK,
    build_product_alignment_pack,
    validate_product_alignment_pack,
)

DEFAULT_OUTPUT = Path("data/knowledge_graph/product_alignment/grade4_mathematics_product_alignment_pack.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/product_alignment/grade4_mathematics_product_alignment_pack_summary.json")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generation-pack", default=str(DEFAULT_GENERATION_PACK))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary-output", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pack = build_product_alignment_pack(Path(args.generation_pack))
    validation = validate_product_alignment_pack(pack)
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
            "valid={} tutor_previews={} study_plan_items={} gamification_award_candidates={}".format(
                str(validation["valid"]).lower(),
                pack["counts"]["tutor_previews"],
                pack["counts"]["study_plan_items"],
                pack["counts"]["gamification_award_candidates"],
            )
        )
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
