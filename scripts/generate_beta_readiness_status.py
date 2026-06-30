#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/beta_readiness_status.json"
OUT_MD = ROOT / "docs/release/beta_readiness_status.md"
EVIDENCE = {
    "remote_ci": ROOT / "docs/release/ci_evidence.json",
    "branch_protection": ROOT / "docs/release/branch_protection_evidence.json",
    "content_gate": ROOT / "docs/beta/beta_content_hard_gate.json",
    "staging_smoke": ROOT / "docs/release/staging_smoke_final_evidence.json",
    "backup_drill": ROOT / "docs/release/backup_drill_evidence.json",
    "restore_drill": ROOT / "docs/release/restore_drill_evidence.json",
    "rollback_drill": ROOT / "docs/release/rollback_drill_evidence.json",
}
PASS_STATUSES = {"green", "verified", "pass", "waived"}


def load_status(path: Path) -> dict:
    if not path.exists():
        return {"status": "missing", "required": True}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "invalid", "error": str(exc), "required": True}


def main() -> int:
    evidence = {name: load_status(path) for name, path in EVIDENCE.items()}
    blockers = [name for name, payload in evidence.items() if payload.get("required", True) and payload.get("status") not in PASS_STATUSES]
    status = "beta_ready" if not blockers else "blocked"
    payload = {"status": status, "blockers": blockers, "evidence": evidence, "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "required": True}
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = ["# Beta Readiness Status", "", f"**Status:** {status}", "", "| Gate | Status |", "|---|---|"]
    for name, item in evidence.items():
        lines.append(f"| {name} | {item.get('status')} |")
    lines.extend(["", "## Blockers", ""])
    lines.extend((f"- {blocker}" for blocker in blockers) if blockers else ["- None"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    return 0 if status == "beta_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
