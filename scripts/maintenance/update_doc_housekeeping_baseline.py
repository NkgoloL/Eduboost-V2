#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from doc_utils import write_json_deterministic


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh the documentation housekeeping ratchet baseline from the current deterministic inventory.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--inventory", default="docs/generated/documentation_inventory.json")
    parser.add_argument("--out", default="docs/documentation/housekeeping_ratchet_baseline.json")
    parser.add_argument("--note", default="Stage 2 baseline captured after deterministic LFS-aware inventory adoption.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    inventory_path = root / args.inventory
    if not inventory_path.exists():
        print(f"Missing inventory: {args.inventory}")
        return 1
    data = json.loads(inventory_path.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    finding_counts = summary.get("finding_counts_by_type", {})
    baseline = {
        "schema_version": "doc-housekeeping-ratchet/v1",
        "baseline_source": args.inventory,
        "note": args.note,
        "max_summary": {
            "markdown_files": int(summary.get("markdown_files", 0)),
            "broken_local_link_count": int(summary.get("broken_local_link_count", 0)),
            "finding_count": int(summary.get("finding_count", 0)),
        },
        "min_summary": {
            "files_with_metadata": int(summary.get("files_with_metadata", 0)),
            "files_with_owner": int(summary.get("files_with_owner", 0)),
            "files_with_source_of_truth": int(summary.get("files_with_source_of_truth", 0)),
        },
        "max_findings_by_type": {str(k): int(v) for k, v in sorted(finding_counts.items())},
        "strict_zero_new_finding_types": True,
    }
    write_json_deterministic(root / args.out, baseline)
    print(f"Updated {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
