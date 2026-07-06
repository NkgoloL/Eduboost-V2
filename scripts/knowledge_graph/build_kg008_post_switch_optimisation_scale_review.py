#!/usr/bin/env python3
"""Build KG-8 post-switch optimisation and scale review artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.domain.knowledge_graph_post_switch_review import (
    DEFAULT_RUNTIME_ACTIVATION_PACK,
    build_post_switch_review_pack,
    validate_post_switch_review_pack,
)

DEFAULT_OUTPUT = Path("data/knowledge_graph/post_switch_review/grade4_mathematics_post_switch_optimisation_scale_review_pack.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/post_switch_review/grade4_mathematics_post_switch_optimisation_scale_review_pack_summary.json")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-activation-pack", type=Path, default=DEFAULT_RUNTIME_ACTIVATION_PACK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    pack = build_post_switch_review_pack(args.runtime_activation_pack)
    validation = validate_post_switch_review_pack(pack)
    summary = {
        "valid": validation["valid"],
        "graph_id": pack["graph_id"],
        "graph_version": pack["graph_version"],
        "runtime_activation_pack_sha256": pack["source"]["runtime_activation_pack_sha256"],
        "counts": pack["counts"],
        "validation": validation,
        "output": str(args.output),
    }
    if args.write:
        write_json(args.output, pack)
        write_json(args.summary, summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"valid={str(validation['valid']).lower()} output={args.output}")
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
