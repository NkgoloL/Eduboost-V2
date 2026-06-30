#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/architecture/legacy_learner_access_guard_report.json"
OUT_MD = ROOT / "docs/architecture/legacy_learner_access_guard_report.md"


def main() -> int:
    rows = []
    for path in sorted((ROOT / "app").rglob("*.py")) if (ROOT / "app").exists() else []:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "assert_can_access_learner" in text:
            rows.append({"path": str(path.relative_to(ROOT)), "count": text.count("assert_can_access_learner")})

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "remaining_legacy_guard_references": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = ["# Legacy Learner Access Guard Report", "", f"Generated at: `{payload['generated_at']}`", "", "| Path | Count |", "|---|---:|"]
    if rows:
        for row in rows:
            lines.append(f"| `{row['path']}` | {row['count']} |")
    else:
        lines.append("| - | 0 |")
    lines.extend(["", "These references are Phase 1/Phase 2 boundary debt unless explicitly wrapped by read/write-specific helpers.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
