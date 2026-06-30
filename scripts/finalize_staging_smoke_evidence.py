#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LATEST_JSON = ROOT / "docs/release/staging_smoke_latest.json"
OUT_JSON = ROOT / "docs/release/staging_smoke_final_evidence.json"
OUT_MD = ROOT / "docs/release/staging_smoke_final_evidence.md"


def main() -> int:
    if LATEST_JSON.exists():
        data = json.loads(LATEST_JSON.read_text(encoding="utf-8"))
        passed = bool(data.get("passed"))
        status = "pass" if passed else "fail"
    else:
        data = {}
        status = "pending_staging_smoke"
    payload = {
        "status": status,
        "source": str(LATEST_JSON.relative_to(ROOT)) if LATEST_JSON.exists() else None,
        "base_url": data.get("base_url"),
        "passed": data.get("passed", False),
        "result_count": len(data.get("results", [])) if isinstance(data.get("results"), list) else 0,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required": True,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Staging Smoke Final Evidence", "", f"**Status:** {status}", "",
        "| Field | Value |", "|---|---|",
        f"| Source | {payload['source'] or 'PENDING'} |",
        f"| Base URL | {payload['base_url'] or 'PENDING'} |",
        f"| Passed | {payload['passed']} |",
        f"| Result count | {payload['result_count']} |",
        f"| Captured at | {payload['captured_at']} |", "",
        "Run `make staging-smoke` and `make staging-smoke-check` against a real staging URL before beta.", "",
    ]), encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    return 0 if status == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
