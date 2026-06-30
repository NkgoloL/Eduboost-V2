#!/usr/bin/env python3
"""Build file-backed promotion readiness manifests for all content scopes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the summary JSON.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override manifest output directory.")
    args = parser.parse_args()

    service = ContentFilePromotionReadinessService(project_root=ROOT)
    summary = service.write_manifests(output_dir=args.output_dir)
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print("Promotion readiness manifests")
        for key, value in summary["summary"].items():
            print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
