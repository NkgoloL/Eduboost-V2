#!/usr/bin/env python3
"""Export a stable, hashable Gate 2R.7 tutor-grounding packet."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.tutor_grounding import build_gate2r7_tutor_packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packet = build_gate2r7_tutor_packet()
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print("Gate 2R.7 tutor packet exported")
        print(f"policy_version={packet['policy_version']}")
        print(f"packet_sha256={packet['packet_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
