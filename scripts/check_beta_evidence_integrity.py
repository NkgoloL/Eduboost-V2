#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

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

PASS_STATUSES = {"pass", "passed", "green", "verified", "success", "waived"}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "missing", "integrity_status": "missing"}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    print("Beta evidence integrity check")

    for gate, path in GATE_FILES.items():
        data = load(path)
        status = str(data.get("status") or "").lower()
        integrity = str(data.get("integrity_status") or "").lower()
        source_type = str(data.get("evidence_source_type") or "").lower()

        if not source_type:
            failures.append(f"{gate}: missing evidence_source_type")
            print(f"- FAIL {gate}: missing evidence_source_type")
            continue

        if status in PASS_STATUSES and integrity != "valid":
            failures.append(f"{gate}: pass-like status without valid integrity")
            print(f"- FAIL {gate}: status={status}, integrity={integrity}")
        else:
            print(f"- PASS {gate}: status={status}, integrity={integrity}, source={source_type}")

    readiness = load(ROOT / "docs/release/beta_readiness_status.json")
    if readiness.get("status") == "beta_ready":
        for gate, data in readiness.get("evidence", {}).items():
            if str(data.get("integrity_status") or "") != "valid":
                failures.append(f"readiness marked beta_ready with invalid gate {gate}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS beta evidence integrity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
