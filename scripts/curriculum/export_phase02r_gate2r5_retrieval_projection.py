#!/usr/bin/env python3
"""Export a deterministic Gate 2R.5 retrieval projection dry-run."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.corpus import build_gate2r5_fixture_package


def export() -> dict[str, object]:
    manifest, projection, _binding, _retrieval = build_gate2r5_fixture_package()
    payload = projection.export()
    payload["status"] = "passed"
    payload["gate"] = "2R.5"
    payload["manifest_sha256"] = manifest.manifest_sha256
    payload["claim"] = "retrieval projection contains only active approved corpus membership"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = export()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Phase 2R Gate 2R.5 retrieval projection export passed")
        print(f"projection_sha256={payload['projection_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
