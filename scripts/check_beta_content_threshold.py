#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/beta/beta_content_threshold_status.json"
MIN_APPROVED = 40

def count_approved() -> int:
    files = [
        ROOT / "docs/caps/grade4_maths_coverage_matrix.md",
        ROOT / "docs/caps/item_bank_status.md",
        ROOT / "docs/release/item_review_log.md",
        ROOT / "docs/beta/item_review_log.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in files if path.exists())
    for pattern in [r"approved items?\D+(\d+)", r"currently approved\D+(\d+)", r"approved\D+(\d+)\s*(?:items?)"]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return len(re.findall(r"\bapproved\b", text, re.IGNORECASE)) if text else 0

def main() -> int:
    approved = count_approved()
    data = {
        "beta_ready": approved >= MIN_APPROVED,
        "approved_items": approved,
        "required_items": MIN_APPROVED,
        "blockers": [] if approved >= MIN_APPROVED else ["insufficient_approved_items"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))
    return 0 if data["beta_ready"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
