#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/release/beta_readiness_status.json"
OUT = ROOT / "docs/release/release_owner_beta_go_no_go_memo.md"


def main() -> int:
    data = json.loads(STATUS.read_text(encoding="utf-8")) if STATUS.exists() else {"status": "missing", "blockers": ["beta_readiness_status_missing"]}
    status = data.get("status", "missing")
    decision = "GO" if status == "beta_ready" else "NO-GO"
    blockers = data.get("blockers") or []

    lines = [
        "# Release-Owner Beta Go/No-Go Memo",
        "",
        f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        f"## Recommendation: {decision}",
        "",
        "## Basis",
        "",
        f"Beta readiness status: `{status}`",
        "",
        "This memo rejects placeholder, local mock, synthetic, and manual-bypass evidence for required beta gates.",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Explicit non-approvals",
        "",
        "This memo does not approve production launch, destructive database changes, consent-table merge, audit_logs drop, public mutating health probes, or synthetic evidence substitution.",
        "",
        "## Release-owner decision",
        "",
        "- [ ] Approved for controlled beta",
        "- [ ] Conditional approval",
        "- [ ] Rejected",
        "",
        "Release owner:",
        "",
        "Date:",
        "",
    ])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
