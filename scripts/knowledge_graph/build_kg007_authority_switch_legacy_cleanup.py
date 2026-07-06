#!/usr/bin/env python3
"""Build the KG-7 authority-switch readiness and legacy-cleanup artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_authority_switch import (
    DEFAULT_PRODUCT_ALIGNMENT_PACK,
    build_authority_switch_readiness_pack,
    validate_authority_switch_readiness_pack,
)

DEFAULT_OUTPUT = Path("data/knowledge_graph/authority_switch/grade4_mathematics_authority_switch_readiness_pack.json")
DEFAULT_SUMMARY = Path("data/knowledge_graph/authority_switch/grade4_mathematics_authority_switch_readiness_pack_summary.json")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-alignment-pack", default=str(DEFAULT_PRODUCT_ALIGNMENT_PACK))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary-output", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pack = build_authority_switch_readiness_pack(Path(args.product_alignment_pack))
    validation = validate_authority_switch_readiness_pack(pack)
    summary = {
        "valid": validation["valid"],
        "graph_id": pack["graph_id"],
        "graph_version": pack["graph_version"],
        "product_alignment_pack_sha256": pack["source"]["product_alignment_pack_sha256"],
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
            "valid={} readiness_checks={} legacy_projection_mappings={} switch_control_edges={}".format(
                str(validation["valid"]).lower(),
                pack["counts"]["authority_readiness_checks"],
                pack["counts"]["legacy_projection_mappings"],
                pack["counts"]["switch_control_edges"],
            )
        )
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
