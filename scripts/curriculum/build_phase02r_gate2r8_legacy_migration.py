#!/usr/bin/env python3
"""Export the Gate 2R.8 legacy migration disposition manifest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.legacy_migration import build_gate2r8_legacy_migration_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = build_gate2r8_legacy_migration_manifest()
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"Gate 2R.8 legacy migration manifest: {manifest['status']}")
        print(f"manifest_sha256={manifest['manifest_sha256']}")
    return 0 if manifest.get("status") == "ready_for_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
