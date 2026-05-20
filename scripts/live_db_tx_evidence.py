from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS_JSON = ROOT / "docs/release/live_db_transaction_evidence_status.json"
STATUS_MD = ROOT / "docs/release/live_db_transaction_evidence_status.md"

SLICES = {
    "auth": {
        "item": "ROUTE-TX-AUTH-001",
        "title": "Auth route transaction live DB evidence",
        "evidence_file": "docs/release/auth_route_transaction_live_db_evidence.md",
        "report_module": "scripts.route_tx_auth_slice",
        "report_function": "write_report",
        "release_check": "make route-tx-auth-slice-release-check",
    },
    "popia": {
        "item": "ROUTE-TX-POPIA-001",
        "title": "POPIA route transaction live DB evidence",
        "evidence_file": "docs/release/popia_route_transaction_live_db_evidence.md",
        "report_module": "scripts.route_tx_popia_slice",
        "report_function": "write_report",
        "release_check": "make route-tx-popia-slice-release-check",
    },
    "diagnostics": {
        "item": "ROUTE-TX-DIAG-001",
        "title": "Diagnostics route transaction live DB evidence",
        "evidence_file": "docs/release/diagnostics_route_transaction_live_db_evidence.md",
        "report_module": "scripts.route_tx_diagnostics_slice",
        "report_function": "write_report",
        "release_check": "make route-tx-diagnostics-slice-release-check",
    },
}

PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}
PASS_VALUES = {"passed", "pass", "green", "ok", "success", "successful"}
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


@dataclass(frozen=True)
class LiveDBEvidence:
    slice: str
    item: str
    route_slice: str
    live_db_evidence_url: str
    test_result: str
    database: str
    commit_sha: str
    verified_by: str
    date_verified: str
    notes: str
    evidence_file: str


@dataclass(frozen=True)
class LiveDBEvidenceRecord:
    evidence: LiveDBEvidence
    status: str
    blockers: list[str]


@dataclass(frozen=True)
class LiveDBEvidenceStatus:
    generated_at: str
    current_commit: str
    status: str
    records: list[LiveDBEvidenceRecord]
    blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _is_pending(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _is_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def _field(text: str, name: str) -> str:
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip().strip("`").strip() if match else ""


def evidence_path(slice_name: str) -> Path:
    if slice_name not in SLICES:
        raise ValueError(f"Unknown transaction slice: {slice_name}")
    return ROOT / SLICES[slice_name]["evidence_file"]


def template_for(slice_name: str) -> str:
    meta = SLICES[slice_name]
    return "\n".join(
        [
            f"# {meta['title']}",
            "",
            f"**Item:** {meta['item']}",
            "",
            f"**Route slice:** {slice_name}",
            "",
            "**Live DB evidence URL:** pending",
            "",
            "**Test result:** pending",
            "",
            "**Database:** pending",
            "",
            "**Commit SHA:** pending",
            "",
            "**Verified by:** pending",
            "",
            "**Date verified:** pending",
            "",
            "**Notes:** pending",
            "",
            "## Required proof",
            "",
            "- Route-level negative tests execute the production route path.",
            "- Injected failures roll back all partial persistence writes.",
            "- Evidence is produced against a real database transaction boundary.",
            "",
            "## No false-closure rule",
            "",
            "This file is not live DB proof while any field remains pending or while test result is not `passed`.",
            "",
        ]
    )


def write_templates() -> None:
    for slice_name in SLICES:
        path = evidence_path(slice_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and f"**Item:** {SLICES[slice_name]['item']}" in path.read_text(encoding="utf-8"):
            continue
        path.write_text(template_for(slice_name), encoding="utf-8")


def read_evidence(slice_name: str) -> LiveDBEvidence:
    write_templates()
    path = evidence_path(slice_name)
    text = path.read_text(encoding="utf-8")
    return LiveDBEvidence(
        slice=slice_name,
        item=SLICES[slice_name]["item"],
        route_slice=_field(text, "Route slice"),
        live_db_evidence_url=_field(text, "Live DB evidence URL"),
        test_result=_field(text, "Test result"),
        database=_field(text, "Database"),
        commit_sha=_field(text, "Commit SHA"),
        verified_by=_field(text, "Verified by"),
        date_verified=_field(text, "Date verified"),
        notes=_field(text, "Notes"),
        evidence_file=SLICES[slice_name]["evidence_file"],
    )


def blockers_for(evidence: LiveDBEvidence) -> list[str]:
    blockers: list[str] = []
    if _is_pending(evidence.route_slice):
        blockers.append("route slice is pending")
    if _is_pending(evidence.live_db_evidence_url) or not _is_url(evidence.live_db_evidence_url):
        blockers.append("live DB evidence URL is pending or invalid")
    if _is_pending(evidence.test_result) or evidence.test_result.strip().lower() not in PASS_VALUES:
        blockers.append("test result must be pass/passed/success/successful/green/ok")
    if _is_pending(evidence.database):
        blockers.append("database is pending")
    if _is_pending(evidence.commit_sha) or not SHA_RE.fullmatch(evidence.commit_sha.strip()):
        blockers.append("commit SHA is pending or invalid")
    if _is_pending(evidence.verified_by):
        blockers.append("verified by is pending")
    if _is_pending(evidence.date_verified):
        blockers.append("date verified is pending")
    return blockers


def read_record(slice_name: str) -> LiveDBEvidenceRecord:
    evidence = read_evidence(slice_name)
    blockers = blockers_for(evidence)
    return LiveDBEvidenceRecord(
        evidence=evidence,
        status="live-db-proof-accepted" if not blockers else "external-blocked",
        blockers=blockers,
    )


def render_evidence(evidence: LiveDBEvidence, status: str) -> str:
    meta = SLICES[evidence.slice]
    return "\n".join(
        [
            f"# {meta['title']}",
            "",
            f"**Item:** {meta['item']}",
            "",
            f"**Route slice:** {evidence.route_slice}",
            "",
            f"**Live DB evidence URL:** {evidence.live_db_evidence_url}",
            "",
            f"**Test result:** {evidence.test_result}",
            "",
            f"**Database:** {evidence.database}",
            "",
            f"**Commit SHA:** {evidence.commit_sha}",
            "",
            f"**Verified by:** {evidence.verified_by}",
            "",
            f"**Date verified:** {evidence.date_verified}",
            "",
            f"**Notes:** {evidence.notes or 'none'}",
            "",
            "## Evidence status",
            "",
            f"`{status}`",
            "",
            "## No false-closure rule",
            "",
            "Live DB proof is accepted only when generated status reports this slice as `live-db-proof-accepted`.",
            "",
        ]
    )


def attach_evidence(
    *,
    slice_name: str,
    evidence_url: str,
    test_result: str,
    database: str,
    commit_sha: str,
    verified_by: str,
    date_verified: str,
    notes: str,
) -> LiveDBEvidenceRecord:
    if slice_name not in SLICES:
        raise ValueError(f"Unknown transaction slice: {slice_name}")
    evidence = LiveDBEvidence(
        slice=slice_name,
        item=SLICES[slice_name]["item"],
        route_slice=slice_name,
        live_db_evidence_url=evidence_url,
        test_result=test_result,
        database=database,
        commit_sha=commit_sha,
        verified_by=verified_by,
        date_verified=date_verified,
        notes=notes,
        evidence_file=SLICES[slice_name]["evidence_file"],
    )
    blockers = blockers_for(evidence)
    status = "live-db-proof-accepted" if not blockers else "external-blocked"
    evidence_path(slice_name).write_text(render_evidence(evidence, status), encoding="utf-8")
    return read_record(slice_name)


def regenerate_dependent_reports() -> None:
    for meta in SLICES.values():
        try:
            module = __import__(meta["report_module"], fromlist=[meta["report_function"]])
            getattr(module, meta["report_function"])()
        except Exception:
            continue

    for module_name, function_name in [
        ("scripts.route_tx_slice_rollup", "write_rollup"),
        ("scripts.release_go_no_go", "write_status"),
        ("scripts.beta_blocker_burndown", "write_plan"),
    ]:
        try:
            module = __import__(module_name, fromlist=[function_name])
            getattr(module, function_name)()
        except Exception:
            continue


def build_status() -> LiveDBEvidenceStatus:
    write_templates()
    records = [read_record(slice_name) for slice_name in SLICES]
    blockers: list[str] = []
    for record in records:
        blockers.extend(f"{record.evidence.slice}: {blocker}" for blocker in record.blockers)

    return LiveDBEvidenceStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="live-db-evidence-complete" if not blockers else "external-blocked",
        records=records,
        blockers=blockers,
    )


def write_status() -> LiveDBEvidenceStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Live DB Transaction Evidence Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Slice | Item | Test result | Database | Commit | Evidence URL | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in status.records:
        evidence = record.evidence
        lines.append(
            f"| `{evidence.slice}` | `{evidence.item}` | `{evidence.test_result}` | `{evidence.database}` | "
            f"`{evidence.commit_sha}` | `{evidence.live_db_evidence_url}` | `{record.status}` |"
        )

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This status validates recorded live DB evidence metadata. It does not run the database tests or verify remote URLs.",
            "",
        ]
    )
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--templates", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--attach", choices=sorted(SLICES))
    parser.add_argument("--evidence-url", default="pending")
    parser.add_argument("--test-result", default="pending")
    parser.add_argument("--database", default="pending")
    parser.add_argument("--commit-sha", default=current_commit())
    parser.add_argument("--verified-by", default="pending")
    parser.add_argument("--date-verified", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--notes", default="attached through LIVE-DB-TX-EVID-001 helper")
    args = parser.parse_args(argv)

    if args.templates:
        write_templates()
        print("live DB evidence templates ready")
        return 0

    if args.attach:
        record = attach_evidence(
            slice_name=args.attach,
            evidence_url=args.evidence_url,
            test_result=args.test_result,
            database=args.database,
            commit_sha=args.commit_sha,
            verified_by=args.verified_by,
            date_verified=args.date_verified,
            notes=args.notes,
        )
        regenerate_dependent_reports()
        status = write_status()
        print(record.status)
        print(status.status)
        if record.status != "live-db-proof-accepted":
            for blocker in record.blockers:
                print(f"- {blocker}")
            return 1
        return 0

    status = write_status()
    print(status.status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
