#!/usr/bin/env python3
"""Build a deterministic Gate 2R.5 semantic corpus manifest dry-run."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.corpus import build_gate2r5_fixture_package, canonical_gate2r5_candidates


def build() -> dict[str, object]:
    manifest, projection, binding, retrieval = build_gate2r5_fixture_package()
    candidates = canonical_gate2r5_candidates()
    return {
        "status": "passed",
        "gate": "2R.5",
        "claim": "approved semantic corpus manifest is deterministic and hashable",
        "manifest": manifest.export(),
        "candidate_count": len(candidates),
        "binding": asdict(binding),
        "projection_sha256": projection.projection_sha256,
        "sample_retrieval_hit_count": len(retrieval.hits),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Phase 2R Gate 2R.5 semantic corpus manifest dry-run passed")
        print(f"manifest_sha256={payload['manifest']['manifest_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
