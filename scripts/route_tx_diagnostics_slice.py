from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS_ROUTER = ROOT / "app/api_v2_routers/diagnostics.py"
TX_ROUTE_INVENTORY_JSON = ROOT / "docs/architecture/tx_route_wiring_inventory.json"
OUT_JSON = ROOT / "docs/release/diagnostics_route_transaction_slice_report.json"
OUT_MD = ROOT / "docs/release/diagnostics_route_transaction_slice_report.md"
GAP_JSON = ROOT / "docs/release/diagnostics_route_transaction_gap_plan.json"
GAP_MD = ROOT / "docs/release/diagnostics_route_transaction_gap_plan.md"
LIVE_DB_EVIDENCE = ROOT / "docs/release/diagnostics_route_transaction_live_db_evidence.md"

DIRECT_DB_MUTATION_METHODS = {"add", "add_all", "commit", "delete", "execute", "flush", "merge", "refresh", "rollback"}
SERVICE_NAME_HINTS = {
    "diagnostic_service",
    "diagnostics_service",
    "diagnostic_session_service",
    "session_service",
    "response_service",
    "mastery_service",
    "assessment_service",
    "item_bank_service",
    "diagnostics",
    "service",
}
MUTATION_NAME_HINTS = {"submit", "response", "session", "diagnostic", "mastery", "attempt"}
TRANSACTION_MARKERS = {
    "TransactionalDiagnosticResponseService",
    "TransactionalDiagnostic",
    "async with self.session.begin",
    "async with session.begin",
    "async with db.begin",
    ".begin()",
}
PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}


@dataclass(frozen=True)
class DiagnosticsRouteSliceFinding:
    route_function: str
    line: int
    selected_from_inventory: bool
    service_delegate_calls: list[str]
    direct_db_mutations: list[str]
    route_source_status: str
    reason: str


@dataclass(frozen=True)
class DiagnosticsRouteTransactionSliceReport:
    generated_at: str
    current_commit: str
    route_file: str
    local_status: str
    live_db_status: str
    selected_route_count: int
    transaction_service_markers_found: list[str]
    findings: list[DiagnosticsRouteSliceFinding]
    blockers: list[str]
    no_false_closure_rules: list[str]


@dataclass(frozen=True)
class DiagnosticsRouteTxGapAction:
    route_function: str
    line: int
    current_status: str
    blocker_reason: str
    implementation_action: str
    verification_action: str
    can_be_closed_by_current_report: bool


@dataclass(frozen=True)
class DiagnosticsRouteTxGapPlan:
    generated_at: str
    current_commit: str
    source_report: str
    source_local_status: str
    source_live_db_status: str
    status: str
    action_count: int
    actions: list[DiagnosticsRouteTxGapAction]
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


def _load_inventory() -> dict[str, Any]:
    if TX_ROUTE_INVENTORY_JSON.exists():
        return json.loads(TX_ROUTE_INVENTORY_JSON.read_text(encoding="utf-8"))
    try:
        from scripts.tx_route_wiring_inventory import write_inventory
        write_inventory()
    except Exception:
        return {"routes": [], "status": "missing-inventory"}
    if TX_ROUTE_INVENTORY_JSON.exists():
        return json.loads(TX_ROUTE_INVENTORY_JSON.read_text(encoding="utf-8"))
    return {"routes": [], "status": "missing-inventory"}


def _selected_route_names() -> set[str]:
    inventory = _load_inventory()
    names: set[str] = set()
    for row in inventory.get("routes") or []:
        if row.get("domain") != "diagnostics":
            continue
        if row.get("mutation_candidate") is True and row.get("status") == "route-transaction-wiring-not-proven":
            name = str(row.get("function_name") or "").strip()
            if name:
                names.add(name)
    return names


def _decorator_text(lines: list[str], node: ast.AST) -> str:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    chunks: list[str] = []
    for decorator in node.decorator_list:
        start = decorator.lineno - 1
        end = decorator.end_lineno or decorator.lineno
        chunks.append("\n".join(lines[start:end]))
    return "\n".join(chunks)


def _is_route(lines: list[str], node: ast.AST) -> bool:
    return "router." in _decorator_text(lines, node)


def _call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _direct_db_mutations(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    mutations: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child)
            if name.startswith("db.") and name.split(".", 1)[1] in DIRECT_DB_MUTATION_METHODS:
                mutations.append(name)
    return sorted(set(mutations))


def _service_delegate_calls(node: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    calls: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child)
            first = name.split(".", 1)[0]
            if first in SERVICE_NAME_HINTS and "." in name:
                calls.append(name)
    return sorted(set(calls))


def _service_marker_source() -> str:
    chunks: list[str] = []
    for root in [ROOT / "app/services", ROOT / "app/modules"]:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            lower = path.as_posix().lower()
            if "diagnostic" not in lower and "assessment" not in lower and "mastery" not in lower:
                continue
            try:
                chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
    return "\n".join(chunks)


def _transaction_service_markers_found() -> list[str]:
    source = _service_marker_source()
    return sorted(marker for marker in TRANSACTION_MARKERS if marker in source)


def _is_pending(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _field(text: str, name: str) -> str:
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip().strip("`").strip() if match else ""


def live_db_template() -> str:
    return "\n".join([
        "# Diagnostics Route Transaction Live DB Evidence",
        "",
        "**Item:** ROUTE-TX-DIAG-001",
        "",
        "**Route slice:** selected diagnostics mutation routes",
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
        "## Required proof",
        "",
        "- Route-level negative tests execute the production diagnostics route path.",
        "- Injected failures roll back response/mastery/audit writes.",
        "- Evidence is produced against a real database transaction boundary.",
        "",
        "## No false-closure rule",
        "",
        "This file is not live DB proof while any field remains pending or while test result is not `passed`.",
        "",
    ])


def write_live_db_template() -> None:
    if LIVE_DB_EVIDENCE.exists() and "**Item:** ROUTE-TX-DIAG-001" in LIVE_DB_EVIDENCE.read_text(encoding="utf-8"):
        return
    LIVE_DB_EVIDENCE.write_text(live_db_template(), encoding="utf-8")


def live_db_status() -> tuple[str, list[str]]:
    write_live_db_template()
    text = LIVE_DB_EVIDENCE.read_text(encoding="utf-8")
    fields = {
        "Live DB evidence URL": _field(text, "Live DB evidence URL"),
        "Test result": _field(text, "Test result"),
        "Database": _field(text, "Database"),
        "Commit SHA": _field(text, "Commit SHA"),
        "Verified by": _field(text, "Verified by"),
        "Date verified": _field(text, "Date verified"),
    }
    blockers: list[str] = []
    for name, value in fields.items():
        if _is_pending(value):
            blockers.append(f"{name} is pending")
    if fields["Live DB evidence URL"] and not fields["Live DB evidence URL"].startswith(("https://", "http://")):
        blockers.append("Live DB evidence URL must be a URL")
    if fields["Test result"].strip().lower() not in {"passed", "pass", "green", "ok"}:
        blockers.append("Test result must be passed/pass/green/ok")
    if fields["Commit SHA"] and not re.fullmatch(r"[0-9a-fA-F]{7,40}", fields["Commit SHA"]):
        blockers.append("Commit SHA must look like a git SHA")
    return ("live-db-proof-accepted" if not blockers else "external-blocked", blockers)


def _route_functions(tree: ast.AST, lines: list[str]) -> list[ast.AsyncFunctionDef | ast.FunctionDef]:
    funcs: list[ast.AsyncFunctionDef | ast.FunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and _is_route(lines, node):
            funcs.append(node)
    return sorted(funcs, key=lambda node: node.lineno)


def build_report() -> DiagnosticsRouteTransactionSliceReport:
    blockers: list[str] = []
    findings: list[DiagnosticsRouteSliceFinding] = []
    selected = _selected_route_names()

    if not DIAGNOSTICS_ROUTER.exists():
        blockers.append("diagnostics router file missing")
        tree: ast.AST = ast.Module(body=[], type_ignores=[])
        lines: list[str] = []
    else:
        source = DIAGNOSTICS_ROUTER.read_text(encoding="utf-8")
        tree = ast.parse(source)
        lines = source.splitlines()

    route_nodes = _route_functions(tree, lines)
    if not selected:
        selected = {node.name for node in route_nodes if any(hint in node.name.lower() for hint in MUTATION_NAME_HINTS)}

    for node in route_nodes:
        if node.name not in selected:
            continue
        delegates = _service_delegate_calls(node)
        mutations = _direct_db_mutations(node)
        if delegates and not mutations:
            status = "route-delegates-to-service-boundary"
            reason = "route delegates to service boundary and has no direct db mutation calls"
        else:
            status = "not-proven"
            reasons: list[str] = []
            if not delegates:
                reasons.append("no diagnostics service delegate call found")
            if mutations:
                reasons.append("direct db mutations present: " + ", ".join(mutations))
            reason = "; ".join(reasons)
            blockers.append(f"{node.name}: {reason}")
        findings.append(DiagnosticsRouteSliceFinding(
            route_function=node.name,
            line=node.lineno,
            selected_from_inventory=node.name in selected,
            service_delegate_calls=delegates,
            direct_db_mutations=mutations,
            route_source_status=status,
            reason=reason,
        ))

    if selected and not findings:
        blockers.append("selected diagnostics routes were not found in router source")

    markers = _transaction_service_markers_found()
    if not markers:
        blockers.append("no diagnostics transactional service markers found")

    live_status, live_blockers = live_db_status()
    local_status = "route-diagnostics-delegation-passing" if not blockers else "route-diagnostics-delegation-not-proven"

    return DiagnosticsRouteTransactionSliceReport(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        route_file="app/api_v2_routers/diagnostics.py",
        local_status=local_status,
        live_db_status=live_status,
        selected_route_count=len(findings),
        transaction_service_markers_found=markers,
        findings=findings,
        blockers=blockers + [f"live-db: {blocker}" for blocker in live_blockers],
        no_false_closure_rules=[
            "Diagnostics route delegation does not prove live database rollback.",
            "Service markers do not prove the production route path by themselves.",
            "ROUTE-TX-DIAG-001 release mode requires local source passing plus live DB evidence.",
            "TX-ROUTE-001 remains open until all mutation route slices are wired and proven.",
        ],
    )


def write_report() -> DiagnosticsRouteTransactionSliceReport:
    report = build_report()
    OUT_JSON.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    lines = [
        "# Diagnostics Route Transaction Slice Report",
        "",
        f"Generated at: `{report.generated_at}`",
        f"Commit: `{report.current_commit}`",
        "",
        f"- Route file: `{report.route_file}`",
        f"- Local status: `{report.local_status}`",
        f"- Live DB status: `{report.live_db_status}`",
        f"- Selected route count: `{report.selected_route_count}`",
        "",
        "## Route findings",
        "",
        "| Route function | Line | Delegate calls | Direct DB mutations | Status |",
        "|---|---:|---|---|---|",
    ]
    for finding in report.findings:
        lines.append(
            f"| `{finding.route_function}` | {finding.line} | "
            f"`{', '.join(finding.service_delegate_calls) or '-'}` | "
            f"`{', '.join(finding.direct_db_mutations) or '-'}` | `{finding.route_source_status}` |"
        )
    lines.extend(["", "## Transaction service markers found", ""])
    if report.transaction_service_markers_found:
        lines.extend(f"- `{marker}`" for marker in report.transaction_service_markers_found)
    else:
        lines.append("- None")
    lines.extend(["", "## Blockers", ""])
    if report.blockers:
        lines.extend(f"- {blocker}" for blocker in report.blockers)
    else:
        lines.append("- None")
    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in report.no_false_closure_rules)
    lines.extend(["", "## Interpretation", "", "This report proves only the local diagnostics route delegation slice when local status is passing. It does not prove live database rollback.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return report


def build_gap_plan() -> DiagnosticsRouteTxGapPlan:
    report = build_report()
    actions: list[DiagnosticsRouteTxGapAction] = []
    for finding in report.findings:
        if finding.route_source_status == "route-delegates-to-service-boundary":
            continue
        actions.append(DiagnosticsRouteTxGapAction(
            route_function=finding.route_function,
            line=finding.line,
            current_status=finding.route_source_status,
            blocker_reason=finding.reason,
            implementation_action=(
                f"Refactor diagnostics route `{finding.route_function}` to delegate mutation work to a diagnostics "
                "application/service boundary that owns the transaction."
            ),
            verification_action=(
                f"Rerun `make route-tx-diagnostics-slice-check` and add a route-level negative test for "
                f"`{finding.route_function}` before accepting local source proof."
            ),
            can_be_closed_by_current_report=False,
        ))
    status = "blocked" if actions or report.local_status != "route-diagnostics-delegation-passing" else "local-source-clear-live-db-still-required"
    return DiagnosticsRouteTxGapPlan(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        source_report="docs/release/diagnostics_route_transaction_slice_report.json",
        source_local_status=report.local_status,
        source_live_db_status=report.live_db_status,
        status=status,
        action_count=len(actions),
        actions=actions,
        no_false_closure_rules=[
            "Do not mark ROUTE-TX-DIAG-001 proven while local_status is route-diagnostics-delegation-not-proven.",
            "Do not close live DB proof from local source reports.",
            "Do not use generated gap plans as implementation evidence.",
        ],
    )


def write_gap_plan() -> DiagnosticsRouteTxGapPlan:
    plan = build_gap_plan()
    GAP_JSON.write_text(json.dumps(asdict(plan), indent=2), encoding="utf-8")
    lines = [
        "# Diagnostics Route Transaction Gap Plan",
        "",
        f"Generated at: `{plan.generated_at}`",
        f"Commit: `{plan.current_commit}`",
        "",
        f"- Source report: `{plan.source_report}`",
        f"- Source local status: `{plan.source_local_status}`",
        f"- Source live DB status: `{plan.source_live_db_status}`",
        f"- Status: `{plan.status}`",
        f"- Action count: `{plan.action_count}`",
        "",
        "## Gap actions",
        "",
        "| Route function | Line | Current status | Reason | Closeable by current report |",
        "|---|---:|---|---|---:|",
    ]
    if plan.actions:
        for action in plan.actions:
            lines.append(f"| `{action.route_function}` | {action.line} | `{action.current_status}` | {action.blocker_reason} | {action.can_be_closed_by_current_report} |")
    else:
        lines.append("| `-` | 0 | `none` | No local source gaps detected | False |")
    lines.extend(["", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in plan.no_false_closure_rules)
    lines.extend(["", "## Interpretation", "", "This plan is a blocker queue. It is not proof that diagnostics route transaction wiring is complete.", ""])
    GAP_MD.write_text("\n".join(lines), encoding="utf-8")
    return plan


__all__ = [
    "DiagnosticsRouteSliceFinding",
    "DiagnosticsRouteTransactionSliceReport",
    "DiagnosticsRouteTxGapAction",
    "DiagnosticsRouteTxGapPlan",
    "build_gap_plan",
    "build_report",
    "live_db_status",
    "write_gap_plan",
    "write_report",
]
