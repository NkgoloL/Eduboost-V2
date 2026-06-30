#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "docs/release/beta_evidence_integrity_repair_report.md"
REPORT_JSON = ROOT / "docs/release/beta_evidence_integrity_repair_report.json"

TRUSTED_BY_GATE = {
    "remote_ci": {"github_actions"},
    "branch_protection": {"github_branch_protection"},
    "content_gate": {"educator_review_log", "release_owner_waiver"},
    "staging_smoke": {"real_staging"},
    "backup_drill": {"real_backup_system"},
    "restore_drill": {"real_restore_drill"},
    "rollback_drill": {"real_rollback_drill"},
    "alertmanager_drill": {"real_alertmanager_notification"},
}

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
INVALID_MARKERS = re.compile(
    r"placeholder|mock|local_mock|manual_bypass|bypass|synthetic|fake|dummy|example\.com|staging\.example\.com",
    re.IGNORECASE,
)


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "status": "missing",
            "required": True,
            "evidence_source_type": "unknown",
            "integrity_status": "missing",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "status": "invalid_json",
            "required": True,
            "evidence_source_type": "unknown",
            "integrity_status": "invalid_json",
            "error": f"{type(exc).__name__}: {exc}",
        }
    if not isinstance(data, dict):
        return {
            "status": "invalid_json_shape",
            "required": True,
            "evidence_source_type": "unknown",
            "integrity_status": "invalid_json_shape",
        }
    return data


def infer_source_type(gate: str, data: dict[str, Any]) -> str:
    explicit = str(data.get("evidence_source_type") or "").strip()
    if explicit:
        return explicit

    status = str(data.get("status") or "").lower()
    payload_text = json.dumps(data, sort_keys=True).lower()

    if gate == "remote_ci" and "github.com" in payload_text and "actions/runs" in payload_text:
        return "github_actions"
    if gate == "branch_protection" and data.get("required_checks"):
        return "github_branch_protection"
    if gate == "content_gate" and status in {"waived"} and data.get("waiver_owner"):
        return "release_owner_waiver"
    if gate == "content_gate" and int(data.get("approved_items", 0) or 0) >= int(data.get("required_items", 40) or 40):
        return "educator_review_log"

    return "unknown"


def has_invalid_markers(data: dict[str, Any]) -> bool:
    text = json.dumps(data, sort_keys=True)
    return bool(INVALID_MARKERS.search(text))


def repair_gate(gate: str, path: Path) -> dict[str, Any]:
    data = load_json(path)
    original_status = str(data.get("status") or "missing")
    source_type = infer_source_type(gate, data)
    trusted_sources = TRUSTED_BY_GATE[gate]
    marker_invalid = has_invalid_markers(data)
    source_trusted = source_type in trusted_sources
    status_pass_like = original_status.lower() in PASS_STATUSES

    integrity_status = "valid" if source_trusted and not marker_invalid else "synthetic_invalid"

    # Missing/pending evidence is not synthetic, but it is still not valid for beta readiness.
    if original_status.lower().startswith("pending") or original_status.lower() in {"missing", "blocked", "fail", "failed"}:
        integrity_status = "pending_real_evidence"
        if marker_invalid:
            integrity_status = "synthetic_invalid"

    repaired = dict(data)
    repaired["evidence_source_type"] = source_type
    repaired["integrity_status"] = integrity_status
    repaired["integrity_checked_at"] = now()
    repaired["trusted_source_required"] = sorted(trusted_sources)

    if status_pass_like and integrity_status != "valid":
        repaired["previous_status"] = original_status
        repaired["status"] = "synthetic_invalid"
        repaired.setdefault("blockers", [])
        blockers = list(repaired.get("blockers") or [])
        if "invalid_or_synthetic_evidence" not in blockers:
            blockers.append("invalid_or_synthetic_evidence")
        repaired["blockers"] = blockers

    # Normalize explicitly missing operational evidence.
    if integrity_status == "pending_real_evidence" and original_status.lower() in {"missing"}:
        repaired["status"] = f"pending_{gate}_evidence"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(repaired, indent=2), encoding="utf-8")
    return {
        "gate": gate,
        "path": str(path.relative_to(ROOT)),
        "original_status": original_status,
        "repaired_status": repaired.get("status"),
        "evidence_source_type": source_type,
        "integrity_status": integrity_status,
        "marker_invalid": marker_invalid,
        "source_trusted": source_trusted,
    }


def write_markdown_report(results: list[dict[str, Any]]) -> None:
    lines = [
        "# Beta Evidence Integrity Repair Report",
        "",
        f"Generated at: `{now()}`",
        "",
        "## Summary",
        "",
        "This repair quarantines placeholder/manual-bypass/local-mock/synthetic evidence and restores truthful beta readiness semantics.",
        "",
        "| Gate | Previous status | Repaired status | Source type | Integrity |",
        "|---|---|---|---|---|",
    ]
    for item in results:
        lines.append(
            f"| {item['gate']} | {item['original_status']} | {item['repaired_status']} | {item['evidence_source_type']} | {item['integrity_status']} |"
        )
    lines.extend([
        "",
        "## Release rule",
        "",
        "Beta readiness is blocked unless every required gate has trusted real evidence or an explicit approved waiver for the content gate only.",
        "",
    ])
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = [repair_gate(gate, path) for gate, path in GATE_FILES.items()]
    REPORT_JSON.write_text(json.dumps({"generated_at": now(), "results": results}, indent=2), encoding="utf-8")
    write_markdown_report(results)
    print(f"Wrote {REPORT_MD.relative_to(ROOT)}")
    print(f"Wrote {REPORT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
