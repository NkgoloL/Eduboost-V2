from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/route_transaction_slice_rollup.json"
OUT_MD = ROOT / "docs/release/route_transaction_slice_rollup.md"
TX_ROUTE_INVENTORY_JSON = ROOT / "docs/architecture/tx_route_wiring_inventory.json"

SLICES = {
    "ROUTE-TX-AUTH-001": {
        "domain": "auth",
        "report": "docs/release/auth_route_transaction_slice_report.json",
        "writer": "scripts.route_tx_auth_slice",
        "write_function": "write_report",
    },
    "ROUTE-TX-POPIA-001": {
        "domain": "popia",
        "report": "docs/release/popia_route_transaction_slice_report.json",
        "writer": "scripts.route_tx_popia_slice",
        "write_function": "write_report",
    },
    "ROUTE-TX-DIAG-001": {
        "domain": "diagnostics",
        "report": "docs/release/diagnostics_route_transaction_slice_report.json",
        "writer": "scripts.route_tx_diagnostics_slice",
        "write_function": "write_report",
    },
}

PASSING_SOURCE_STATUSES = {"route-delegates-to-service-boundary", "route-delegates-to-auth-service"}


@dataclass(frozen=True)
class RouteTxSliceStatus:
    id: str
    domain: str
    report_file: str
    exists: bool
    local_status: str
    live_db_status: str
    selected_route_count: int
    local_gap_count: int
    live_db_gap_count: int
    blockers: list[str]
    release_ready: bool


@dataclass(frozen=True)
class RouteTxSliceRollup:
    generated_at: str
    current_commit: str
    status: str
    total_selected_routes: int
    local_source_gap_count: int
    live_db_gap_count: int
    inventory_unproven_route_count: int
    slices: list[RouteTxSliceStatus]
    blockers: list[str]
    no_false_closure_rules: list[str]


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


def _attempt_generate_slice(meta: dict[str, str]) -> None:
    path = ROOT / meta["report"]
    if path.exists():
        return
    try:
        module = __import__(meta["writer"], fromlist=[meta["write_function"]])
        getattr(module, meta["write_function"])()
    except Exception:
        return


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _read_report(meta: dict[str, str]) -> dict[str, Any]:
    _attempt_generate_slice(meta)
    return _read_json(ROOT / meta["report"])


def _inventory_unproven_count() -> int:
    payload = _read_json(TX_ROUTE_INVENTORY_JSON)
    count = 0
    for row in payload.get("routes") or []:
        if row.get("mutation_candidate") is True and row.get("status") == "route-transaction-wiring-not-proven":
            count += 1
    return count


def _local_gap_count(report: dict[str, Any]) -> int:
    findings = report.get("findings") or []
    if not findings and str(report.get("local_status") or "").endswith("not-proven"):
        return 1
    gaps = 0
    for finding in findings:
        source_status = str(finding.get("route_source_status") or finding.get("status") or "")
        if source_status not in PASSING_SOURCE_STATUSES:
            gaps += 1
    return gaps


def _live_db_gap_count(report: dict[str, Any]) -> int:
    return 0 if report.get("live_db_status") == "live-db-proof-accepted" else 1


def build_rollup() -> RouteTxSliceRollup:
    slices: list[RouteTxSliceStatus] = []
    blockers: list[str] = []

    for slice_id, meta in SLICES.items():
        report = _read_report(meta)
        exists = bool(report)
        local_status = str(report.get("local_status") or "missing-report")
        live_db_status = str(report.get("live_db_status") or "missing-report")
        selected_count = int(report.get("selected_route_count") or len(report.get("findings") or []))
        local_gaps = _local_gap_count(report) if exists else 1
        live_gaps = _live_db_gap_count(report) if exists else 1
        slice_blockers = list(report.get("blockers") or [])
        if not exists:
            slice_blockers.append("slice report missing")
        if local_gaps:
            slice_blockers.append(f"{local_gaps} local route-source gap(s) remain")
        if live_gaps:
            slice_blockers.append("live DB rollback evidence missing")
        release_ready = exists and local_gaps == 0 and live_gaps == 0
        if not release_ready:
            blockers.append(f"{slice_id}: not release-ready")
        slices.append(
            RouteTxSliceStatus(
                id=slice_id,
                domain=meta["domain"],
                report_file=meta["report"],
                exists=exists,
                local_status=local_status,
                live_db_status=live_db_status,
                selected_route_count=selected_count,
                local_gap_count=local_gaps,
                live_db_gap_count=live_gaps,
                blockers=slice_blockers,
                release_ready=release_ready,
            )
        )

    local_total = sum(item.local_gap_count for item in slices)
    live_total = sum(item.live_db_gap_count for item in slices)
    selected_total = sum(item.selected_route_count for item in slices)
    inventory_unproven = _inventory_unproven_count()
    status = "route-transaction-slices-release-ready" if not (local_total or live_total or inventory_unproven) else "blocked"

    return RouteTxSliceRollup(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status=status,
        total_selected_routes=selected_total,
        local_source_gap_count=local_total,
        live_db_gap_count=live_total,
        inventory_unproven_route_count=inventory_unproven,
        slices=slices,
        blockers=blockers,
        no_false_closure_rules=[
            "Do not close TX-ROUTE-001 while any slice local source gap remains.",
            "Do not close TX-ROUTE-001 while any live DB evidence gap remains.",
            "Do not treat slice source scans as live transaction rollback proof.",
            "Do not mark production route transaction proof complete from documentation rollups alone.",
        ],
    )


def write_rollup() -> RouteTxSliceRollup:
    rollup = build_rollup()
    OUT_JSON.write_text(json.dumps(asdict(rollup), indent=2), encoding="utf-8")
    lines = [
        "# Route Transaction Slice Rollup",
        "",
        f"Generated at: `{rollup.generated_at}`",
        f"Commit: `{rollup.current_commit}`",
        "",
        f"**Status:** `{rollup.status}`",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Total selected routes | {rollup.total_selected_routes} |",
        f"| Local source gaps | {rollup.local_source_gap_count} |",
        f"| Live DB evidence gaps | {rollup.live_db_gap_count} |",
        f"| Inventory unproven mutation routes | {rollup.inventory_unproven_route_count} |",
        "",
        "## Slice status",
        "",
        "| Slice | Domain | Local status | Live DB status | Selected routes | Local gaps | Live DB gaps | Release ready |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for item in rollup.slices:
        lines.append(
            f"| `{item.id}` | `{item.domain}` | `{item.local_status}` | `{item.live_db_status}` | "
            f"{item.selected_route_count} | {item.local_gap_count} | {item.live_db_gap_count} | {item.release_ready} |"
        )
    lines.extend(["", "## Blockers", ""])
    lines.extend([f"- {blocker}" for blocker in rollup.blockers] or ["- None"])
    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in rollup.no_false_closure_rules)
    lines.extend(["", "## Interpretation", "", "This rollup reconciles route transaction slice status. It is not production route transaction closure.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return rollup


__all__ = ["RouteTxSliceRollup", "RouteTxSliceStatus", "build_rollup", "write_rollup"]
