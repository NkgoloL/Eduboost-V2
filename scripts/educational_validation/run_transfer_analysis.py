#!/usr/bin/env python3
"""Educational Transfer Validity CLI Runner (LEV-WS07).

Executes near-transfer and far-transfer validity analysis over student assessment records.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.services.educational_validation.transfer import compute_transfer_matrix


def main() -> None:
    parser = argparse.ArgumentParser(description="Run educational transfer validity analysis.")
    parser.add_argument("--data", required=True, help="Path to JSON dataset with transfer_records")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: file not found {data_path}", file=sys.stderr)
        sys.exit(2)

    payload = json.loads(data_path.read_text())
    records = payload.get("transfer_records", [])
    if not records:
        print("Error: No transfer_records found in data file.", file=sys.stderr)
        sys.exit(2)

    matrix_report = compute_transfer_matrix(records)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(matrix_report, indent=2) + "\n")

    print(json.dumps(matrix_report, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
