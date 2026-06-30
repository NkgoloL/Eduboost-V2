#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/beta_readiness_status.json"
OUT_MD = ROOT / "docs/release/beta_readiness_status.md"

GATE_FILES = {
    "remote_ci": ROOT / "docs/release/ci_evidence.json",
    "branch_protection": ROOT / "docs/release/branch_protection_evidence.json",
    "content_gate": ROOT / "docs/beta/beta_content_hard_gate.json",
    "staging_smoke": ROOT / "docs/release/staging_smoke_final_evidence.json",
    "backup_drill": ROOT / "docs/release/backup_drill_evidence.json",
    "restore_drill": ROOT / "docs/release/restore_drill_evidence.json",
    "rollback_drill": ROOT / "docs/release/rollback_drill_evidence.json",
    "alertmanager_drill": ROOT / "docs/release/alertmanager_drill_evidence.json",
}

VALID_STATUSES = {"pass", "green", "verified", "waived"}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "missing", "integrity_status": "missing", "required": True}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "invalid_json", "integrity_status": "invalid_json", "error": str(exc), "required": True}


def gate_is_ready(gate: str, data: dict[str, Any]) -> bool:
    status = str(data.get("status") or "").lower()
    integrity = str(data.get("integrity_status") or "").lower()
    if gate == "content_gate" and status == "waived" and integrity == "valid":
        return True
    return status in VALID_STATUSES and integrity == "valid"


def main() -> int:
    evidence = {gate: load(path) for gate, path in GATE_FILES.items()}
    blockers = [gate for gate, data in evidence.items() if data.get("required", True) and not gate_is_ready(gate, data)]
    status = "beta_ready" if not blockers else "blocked"
    payload = {
        "status": status,
        "blockers": blockers,
        "evidence": evidence,
        "captured_at": now(),
        "required": True,
        "truth_rule": "required gates must have status pass/green/verified/waived and integrity_status valid",
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Beta Readiness Status",
        "",
        f"**Status:** {status}",
        "",
        "| Gate | Status | Integrity | Source type |",
        "|---|---|---|---|",
    ]
    for gate, data in evidence.items():
        lines.append(f"| {gate} | {data.get('status')} | {data.get('integrity_status')} | {data.get('evidence_source_type', 'unknown')} |")
    lines.extend(["", "## Blockers", ""])
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- None")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    return 0 if status == "beta_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
