#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_DRILLS = {"backup", "restore", "rollback", "alertmanager"}


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "pass", "passed", "success"}


def main() -> int:
    drill = os.getenv("OPERATIONAL_DRILL", "").strip().lower()
    if drill not in VALID_DRILLS:
        print(f"Set OPERATIONAL_DRILL to one of: {', '.join(sorted(VALID_DRILLS))}")
        return 2
    result = os.getenv("OPERATIONAL_DRILL_RESULT", "").strip()
    evidence_url = os.getenv("OPERATIONAL_DRILL_EVIDENCE_URL", "").strip()
    operator = os.getenv("OPERATIONAL_DRILL_OPERATOR", "").strip()
    notes = os.getenv("OPERATIONAL_DRILL_NOTES", "").strip()
    passed = truthy(result) and bool(evidence_url or notes)
    status = "pass" if passed else f"pending_{drill}_evidence"
    out_json = ROOT / f"docs/release/{drill}_drill_evidence.json"
    out_md = ROOT / f"docs/release/{drill}_drill_evidence.md"
    payload = {
        "drill": drill,
        "status": status,
        "result": result,
        "evidence_url": evidence_url,
        "operator": operator,
        "notes": notes,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required": True,
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text("\n".join([
        f"# {drill.title()} Drill Evidence", "", f"**Status:** {status}", "",
        "| Field | Value |", "|---|---|",
        f"| Result | {result or 'PENDING'} |",
        f"| Evidence URL/path | {evidence_url or 'PENDING'} |",
        f"| Operator | {operator or 'PENDING'} |",
        f"| Notes | {notes or 'PENDING'} |",
        f"| Captured at | {payload['captured_at']} |", "",
    ]), encoding="utf-8")
    print(f"Wrote {out_md.relative_to(ROOT)}")
    print(f"Wrote {out_json.relative_to(ROOT)}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
