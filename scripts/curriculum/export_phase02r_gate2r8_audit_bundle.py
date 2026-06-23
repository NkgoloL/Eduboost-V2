#!/usr/bin/env python3
"""Export the Gate 2R.8 audit bundle."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.phase02r_closure import build_gate2r8_audit_bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    bundle = build_gate2r8_audit_bundle(ROOT)
    if args.json:
        print(json.dumps(bundle, indent=2, sort_keys=True))
    else:
        status = bundle["closure_readiness"]["status"]
        print(f"Gate 2R.8 audit bundle: {status}")
        print(f"audit_bundle_sha256={bundle['audit_bundle_sha256']}")
    return 0 if bundle["closure_readiness"]["status"] == "ready_for_candidate_closure_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
