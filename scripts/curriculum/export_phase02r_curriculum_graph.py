#!/usr/bin/env python3
"""Export a deterministic Gate 2R.4 curriculum graph snapshot."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.graph import export_gate2r4_reference_graph  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output", type=Path, help="write JSON export to this path")
    args = parser.parse_args()

    payload = export_gate2r4_reference_graph()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    if args.json or not args.output:
        print(rendered, end="")
    else:
        print(f"wrote Gate 2R.4 graph export: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
