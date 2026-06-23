#!/usr/bin/env python3
"""Build a deterministic Gate 2R.7 grounded tutor response fixture."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.tutor_grounding import build_gate2r7_fixture_response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    response = build_gate2r7_fixture_response()
    if args.json:
        print(json.dumps(response.export(), indent=2, sort_keys=True))
    else:
        print("Gate 2R.7 grounded tutor fixture built")
        print(f"tutor_message_id={response.tutor_message_id}")
        print(f"response_status={response.response_status}")
        print(f"provenance_sha256={response.provenance_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
