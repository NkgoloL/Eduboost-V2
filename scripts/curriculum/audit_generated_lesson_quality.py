#!/usr/bin/env python3
"""Read-only audit for generated scope lesson quality and quarantine status."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.content_file_lesson_quality import ContentFileLessonQualityService


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", help="Audit one scope instead of all scopes.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--write-manifests", action="store_true", help="Write quarantine manifests to data/generated/quality_manifests/.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override manifest output directory.")
    args = parser.parse_args()

    service = ContentFileLessonQualityService(project_root=ROOT)
    if args.scope_id:
        result = service.audit_scope(args.scope_id)
        payload = service._scope_manifest(result)
        passed = result.passed
    else:
        if args.write_manifests:
            payload = service.write_manifests(output_dir=args.output_dir)
        else:
            payload = service.build_all()
        passed = payload["summary"]["lesson_layers_quarantined"] == 0

    if args.json or args.scope_id:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.write_manifests:
        print("Lesson quality manifests")
        for key, value in payload["summary"].items():
            print(f"  {key}: {value}")
    else:
        print("Lesson quality audit")
        for key, value in payload["summary"].items():
            print(f"  {key}: {value}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
