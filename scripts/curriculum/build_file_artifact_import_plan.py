#!/usr/bin/env python3
"""Build a DB import plan manifest for generated scope files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.content_file_artifact_import import ContentFileArtifactImportService

DEFAULT_OUTPUT = ROOT / "data" / "generated" / "import_manifests" / "all_scopes_file_artifact_import_plan.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", action="append", default=None, help="Scope to include. Repeatable. Defaults to all scopes.")
    parser.add_argument("--status", action="append", default=None, help="Registry status to include, for example review. Repeatable.")
    parser.add_argument("--max-records-per-layer", type=int, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    service = ContentFileArtifactImportService(project_root=ROOT)
    batch = service.plan_scope_imports(
        scope_ids=args.scope_id,
        statuses=set(args.status) if args.status else None,
        max_records_per_layer=args.max_records_per_layer,
    )
    manifest = batch.to_manifest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    else:
        summary = manifest["summary"]
        print("Generated file artifact import plan")
        print(f"  scope_count: {summary['scope_count']}")
        print(f"  stage_unlocked: {summary['stage_unlocked']}")
        print(f"  production_unlocked: {summary['production_unlocked']}")
        print(f"  total_records: {summary['total_records']}")
        print(f"  scopes_with_errors: {summary['scopes_with_errors']}")
        print(f"  output: {args.output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
