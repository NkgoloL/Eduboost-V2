#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_JSON = ROOT / "docs/beta/beta_content_threshold_status.json"
HARD_GATE_JSON = ROOT / "docs/beta/beta_content_hard_gate.json"
HARD_GATE_MD = ROOT / "docs/beta/beta_content_hard_gate.md"
MIN_APPROVED = int(os.getenv("BETA_MIN_APPROVED_ITEMS", "40"))


def load_status() -> dict:
    if not STATUS_JSON.exists():
        return {"beta_ready": False, "approved_items": 0, "required_items": MIN_APPROVED, "blockers": ["missing_beta_content_threshold_status"]}
    return json.loads(STATUS_JSON.read_text(encoding="utf-8"))


def main() -> int:
    status = load_status()
    approved = int(status.get("approved_items", 0))
    required = int(status.get("required_items", MIN_APPROVED))
    waiver = os.getenv("BETA_CONTENT_GATE_WAIVER", "").strip()
    waiver_owner = os.getenv("BETA_CONTENT_GATE_WAIVER_OWNER", "").strip()
    passed = approved >= required
    waived = bool(waiver and waiver_owner)
    final_status = "pass" if passed else "waived" if waived else "blocked"
    payload = {
        "status": final_status,
        "approved_items": approved,
        "required_items": required,
        "waiver": waiver,
        "waiver_owner": waiver_owner,
        "blockers": [] if passed or waived else ["insufficient_approved_items"],
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required": True,
    }
    HARD_GATE_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    HARD_GATE_MD.write_text("\n".join([
        "# Beta Content Hard Gate", "", f"**Status:** {final_status}", "",
        "| Field | Value |", "|---|---|",
        f"| Approved items | {approved} |",
        f"| Required items | {required} |",
        f"| Waiver | {waiver or 'None'} |",
        f"| Waiver owner | {waiver_owner or 'None'} |",
        f"| Blockers | {', '.join(payload['blockers']) if payload['blockers'] else 'None'} |",
        f"| Captured at | {payload['captured_at']} |", "",
    ]), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if final_status in {"pass", "waived"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
