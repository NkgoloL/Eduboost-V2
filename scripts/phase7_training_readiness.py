#!/usr/bin/env python3
"""Validate an approved Phase 7 manifest before invoking LoRA/QLoRA training."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest.get("status") != "approved":
        raise SystemExit("Training manifest is not approved")
    dataset = Path(args.dataset)
    if not dataset.is_file():
        raise SystemExit(f"Dataset not found: {dataset}")
    if manifest.get("dataset_sha256") in {None, ""}:
        raise SystemExit("Approved manifest has no dataset SHA-256")
    print(json.dumps({
        "status": "ready",
        "dataset_version": manifest.get("dataset_version"),
        "artifact_count": manifest.get("artifact_count"),
        "dataset": str(dataset),
        "training_executed": False,
        "dry_run": bool(args.dry_run),
    }, indent=2, sort_keys=True))
    if not args.dry_run:
        raise SystemExit("Phase 7 wrapper validates readiness only; invoke controlled training separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
