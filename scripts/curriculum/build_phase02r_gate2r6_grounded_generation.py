#!/usr/bin/env python3
"""Build deterministic Gate 2R.6 grounded lesson and assessment artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.generation import build_gate2r6_fixture_artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--artifact-type", choices=["lesson", "assessment", "lesson_with_assessment", "worked_example"], default="lesson_with_assessment")
    args = parser.parse_args()
    artifact = build_gate2r6_fixture_artifact(args.artifact_type)
    payload = artifact.export()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Gate 2R.6 grounded generation artifact built: {artifact.artifact_id}")
        print(f"status={artifact.status}")
        print(f"artifact_sha256={artifact.artifact_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
